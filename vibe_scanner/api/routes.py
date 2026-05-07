import uuid
import logging
import ipaddress
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, HttpUrl, field_validator

from .dependencies import get_db
from ..db.models import Scan, Finding, ScanStatus
from ..scanner.engine import ScanEngine
from ..vulnerabilities.web.headers import SecurityHeadersCheck
from ..vulnerabilities.auth.basic_auth import BasicAuthCheck
from ..vulnerabilities.ai.agent_auth import AgentAuthorityEscalation, PromptInjectionSurface
from ..reporting.pdf import PDFReportGenerator
from ..db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scans"])


# Pydantic models
class ScanCreate(BaseModel):
    target_url: HttpUrl

    @field_validator("target_url", mode="before")
    @classmethod
    def validate_target_url(cls, v):
        """Validate target URL against SSRF attacks and private IP ranges."""
        if isinstance(v, str):
            try:
                parsed = urlparse(v)
                
                # Reject potentially dangerous schemes
                if parsed.scheme not in ("http", "https"):
                    raise ValueError(f"Only HTTP and HTTPS schemes are allowed, got: {parsed.scheme}")
                
                # Prevent SSRF: reject private and loopback IPs
                try:
                    ip = ipaddress.ip_address(parsed.hostname)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                        raise ValueError(
                            f"Access to private/reserved IP addresses is not allowed: {parsed.hostname}"
                        )
                except ValueError as e:
                    # Could be a domain name (not an IP) - that's fine
                    if "does not appear to be an IPv4 or IPv6 address" not in str(e):
                        raise
                
                # Reject suspicious domains
                hostname = parsed.hostname or ""
                if hostname in ("localhost", "127.0.0.1", "::1"):
                    raise ValueError("Scanning localhost is not allowed")
                
            except Exception as e:
                raise ValueError(f"Invalid target URL: {e}")
        
        return v


class ScanResponse(BaseModel):
    id: str
    status: str
    target_url: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class FindingResponse(BaseModel):
    id: str
    name: str
    severity: str
    category: str
    description: str
    location: Optional[str] = None


class ScanDetailsResponse(BaseModel):
    id: str
    target_url: str
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    findings_count: int
    findings: list[FindingResponse]


async def run_scan_background(scan_id: str) -> None:
    """
    Run scan in background task with proper AsyncSession management.
    IMPORTANT: Creates a fresh AsyncSession for the background task,
    not reusing the request context's session.
    """
    try:
        # Create a fresh session for this background task
        async with AsyncSessionLocal() as session:
            scan_engine = ScanEngine(session, scan_id)
            
            # Register vulnerability check plugins
            scan_engine.register_plugin(SecurityHeadersCheck)
            scan_engine.register_plugin(BasicAuthCheck)
            scan_engine.register_plugin(AgentAuthorityEscalation)
            scan_engine.register_plugin(PromptInjectionSurface)
            
            # Run the scan
            await scan_engine.run()
            
    except Exception as e:
        logger.error(f"Background scan task failed for {scan_id}: {e}", exc_info=True)
        # Attempt to mark scan as failed
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Scan).where(Scan.id == uuid.UUID(scan_id))
                )
                scan = result.scalar_one_or_none()
                if scan:
                    scan.status = ScanStatus.FAILED
                    await session.commit()
        except Exception as update_error:
            logger.error(f"Failed to update scan status to FAILED: {update_error}")


@router.post("/scans/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_in: ScanCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Create a new security scan for the provided target URL.
    The scan runs asynchronously in the background.
    """
    try:
        # Validate URL is accessible
        scan_url = str(scan_in.target_url)
        
        # Create scan record
        new_scan = Scan(
            target_url=scan_url,
            status=ScanStatus.PENDING
        )
        db.add(new_scan)
        await db.commit()
        await db.refresh(new_scan)
        
        # Schedule background task - pass only scan_id, not db session
        background_tasks.add_task(run_scan_background, str(new_scan.id))
        
        logger.info(f"Scan created: {new_scan.id} for {scan_url}")
        
        return {
            "id": str(new_scan.id),
            "status": new_scan.status,
            "target_url": new_scan.target_url,
            "message": "Scan queued. Check status for progress."
        }
        
    except ValueError as e:
        logger.warning(f"Invalid scan request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating scan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan"
        )


@router.get("/scans/", response_model=list[ScanResponse])
async def get_scans(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Get list of scans with pagination.
    Results are ordered by most recent first.
    """
    try:
        if limit > 100:
            limit = 100  # Prevent excessive data transfer
        if skip < 0 or limit < 1:
            raise ValueError("Invalid pagination parameters")
        
        result = await db.execute(
            select(Scan)
            .order_by(Scan.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        scans = result.scalars().all()
        
        return [
            {
                "id": str(scan.id),
                "target_url": scan.target_url,
                "status": scan.status,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "critical_count": scan.critical_count,
                "high_count": scan.high_count,
                "medium_count": scan.medium_count,
                "low_count": scan.low_count,
            }
            for scan in scans
        ]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving scans: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scans"
        )


@router.get("/scans/{scan_id}", response_model=ScanDetailsResponse)
async def get_scan_status(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get detailed information about a specific scan including all findings.
    """
    try:
        # Validate UUID format
        try:
            scan_uuid = uuid.UUID(scan_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scan ID format"
            )
        
        result = await db.execute(
            select(Scan)
            .options(selectinload(Scan.findings))
            .where(Scan.id == scan_uuid)
        )
        scan = result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        return {
            "id": str(scan.id),
            "target_url": scan.target_url,
            "status": scan.status,
            "created_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "findings_count": len(scan.findings),
            "findings": [
                {
                    "id": str(f.id),
                    "name": f.name,
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "location": f.location,
                }
                for f in scan.findings
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scan {scan_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan"
        )


@router.get("/scans/{scan_id}/report/pdf")
async def get_pdf_report(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """
    Generate and return a PDF report for a completed scan.
    This runs synchronously - for large scans, should be moved to async task.
    """
    try:
        # Validate UUID format
        try:
            scan_uuid = uuid.UUID(scan_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scan ID format"
            )
        
        result = await db.execute(
            select(Scan)
            .options(selectinload(Scan.findings))
            .where(Scan.id == scan_uuid)
        )
        scan = result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        if scan.status != ScanStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scan must be completed before generating report. Current status: {scan.status}"
            )
        
        # Generate PDF
        generator = PDFReportGenerator(
            scan_data={
                "id": str(scan.id),
                "target_url": scan.target_url
            },
            findings=scan.findings
        )
        
        filename = f"report_{scan.id}.pdf"
        generator.generate(filename)
        
        logger.info(f"PDF report generated for scan {scan.id}")
        
        return FileResponse(
            filename,
            media_type="application/pdf",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report for {scan_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF report"
        )
