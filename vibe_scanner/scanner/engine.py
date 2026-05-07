import asyncio
import logging
from typing import List, Type, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db.models import Scan, Finding, ScanStatus
from .crawler import SmartCrawler
from ..vulnerabilities.base import VulnerabilityCheck, ScanContext, VulnerabilityIssue

logger = logging.getLogger(__name__)


class ScanEngineError(Exception):
    """Base exception for scan engine errors."""
    pass


class ScanNotFoundError(ScanEngineError):
    """Raised when scan ID cannot be found."""
    pass


class CrawlError(ScanEngineError):
    """Raised when crawling fails."""
    pass


class VulnerabilityCheckError(ScanEngineError):
    """Raised when a vulnerability check fails."""
    pass


class ScanEngine:
    """
    Main scanning engine that orchestrates crawling and vulnerability checks.
    """
    
    def __init__(self, db: AsyncSession, scan_id: str):
        self.db = db
        self.scan_id = scan_id
        self.plugins: List[Type[VulnerabilityCheck]] = []

    def register_plugin(self, plugin_cls: Type[VulnerabilityCheck]) -> None:
        """Register a vulnerability check plugin."""
        if not issubclass(plugin_cls, VulnerabilityCheck):
            raise ValueError(f"{plugin_cls} is not a VulnerabilityCheck subclass")
        self.plugins.append(plugin_cls)
        logger.debug(f"Registered plugin: {plugin_cls.__name__}")

    async def run(self) -> None:
        """
        Execute the security scan:
        1. Fetch scan configuration
        2. Crawl target website
        3. Run vulnerability checks on each page
        4. Save findings to database
        5. Update scan status
        """
        try:
            # 1. Fetch and validate scan
            scan = await self._fetch_scan()
            logger.info(f"Starting scan {self.scan_id} for {scan.target_url}")
            
            # 2. Update status to RUNNING
            scan.status = ScanStatus.RUNNING
            scan.started_at = datetime.utcnow()
            await self.db.commit()
            
            # 3. Crawl target website
            try:
                pages = await self._crawl_target(scan.target_url)
            except CrawlError as e:
                logger.error(f"Crawling failed: {e}")
                scan.status = ScanStatus.FAILED
                await self.db.commit()
                return
            
            if not pages:
                logger.warning(f"No pages crawled for {scan.target_url}")
                scan.status = ScanStatus.COMPLETED
                scan.completed_at = datetime.utcnow()
                await self.db.commit()
                return
            
            logger.info(f"Crawled {len(pages)} pages")
            
            # 4. Run vulnerability checks
            findings = await self._run_vulnerability_checks(pages)
            logger.info(f"Found {len(findings)} total findings")
            
            # 5. Save findings to database
            await self._save_findings(scan, findings)
            
            # 6. Update scan completion status
            metrics = self._calculate_metrics(findings)
            scan.status = ScanStatus.COMPLETED
            scan.completed_at = datetime.utcnow()
            scan.critical_count = metrics["CRITICAL"]
            scan.high_count = metrics["HIGH"]
            scan.medium_count = metrics["MEDIUM"]
            scan.low_count = metrics["LOW"]
            
            await self.db.commit()
            logger.info(f"Scan {self.scan_id} completed successfully")
            
        except ScanNotFoundError as e:
            logger.error(f"Scan not found: {e}")
        except ScanEngineError as e:
            logger.error(f"Scan engine error: {e}")
            await self._mark_scan_failed()
        except Exception as e:
            logger.error(f"Unexpected error during scan: {e}", exc_info=True)
            await self._mark_scan_failed()

    async def _fetch_scan(self) -> Scan:
        """Fetch and validate the scan record."""
        try:
            result = await self.db.execute(
                select(Scan).where(Scan.id == self.scan_id)
            )
            scan = result.scalar_one_or_none()
            
            if not scan:
                raise ScanNotFoundError(f"Scan {self.scan_id} not found in database")
            
            return scan
        except Exception as e:
            if isinstance(e, ScanNotFoundError):
                raise
            raise ScanEngineError(f"Failed to fetch scan: {e}")

    async def _crawl_target(self, target_url: str) -> List:
        """Crawl the target website."""
        try:
            crawler = SmartCrawler(target_url)
            pages = await crawler.crawl()
            return pages
        except asyncio.TimeoutError:
            raise CrawlError("Crawl operation timed out")
        except Exception as e:
            raise CrawlError(f"Crawling failed: {e}")

    async def _run_vulnerability_checks(self, pages: List) -> List[VulnerabilityIssue]:
        """Run all registered vulnerability checks on crawled pages."""
        total_findings = []
        
        # Instantiate all plugins
        active_checks = [Plugin() for Plugin in self.plugins]
        
        if not active_checks:
            logger.warning("No vulnerability checks registered")
            return []
        
        for url, response, soup in pages:
            try:
                context = ScanContext(
                    target_url=url,
                    session=response,
                    soup=soup
                )
                
                # Run each check and collect findings
                for check in active_checks:
                    try:
                        findings = await check.run(context)
                        total_findings.extend(findings)
                        logger.debug(
                            f"Check '{check.__class__.__name__}' on {url}: "
                            f"{len(findings)} findings"
                        )
                    except asyncio.TimeoutError:
                        logger.warning(
                            f"Check '{check.__class__.__name__}' timed out on {url}"
                        )
                    except VulnerabilityCheckError as e:
                        logger.error(
                            f"Check '{check.__class__.__name__}' error on {url}: {e}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Unexpected error in check '{check.__class__.__name__}' "
                            f"on {url}: {type(e).__name__}: {e}"
                        )
                        
            except Exception as e:
                logger.error(f"Error processing page {url}: {e}")
        
        return total_findings

    async def _save_findings(self, scan: Scan, findings: List[VulnerabilityIssue]) -> None:
        """Save vulnerability findings to database."""
        try:
            for issue in findings:
                finding = Finding(
                    scan_id=scan.id,
                    name=issue.name,
                    severity=issue.severity,
                    category=issue.category,
                    description=issue.description,
                    evidence=issue.evidence,
                    recommendation=issue.recommendation,
                    location=issue.location,
                )
                self.db.add(finding)
            
            await self.db.commit()
            logger.info(f"Saved {len(findings)} findings to database")
        except Exception as e:
            logger.error(f"Failed to save findings: {e}", exc_info=True)
            raise ScanEngineError(f"Failed to save findings: {e}")

    def _calculate_metrics(self, findings: List[VulnerabilityIssue]) -> dict:
        """Calculate severity metrics from findings."""
        metrics = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for finding in findings:
            severity = finding.severity
            if severity in metrics:
                metrics[severity] += 1
            else:
                logger.warning(f"Unknown severity level: {severity}")
        
        return metrics

    async def _mark_scan_failed(self) -> None:
        """Mark the scan as failed."""
        try:
            result = await self.db.execute(
                select(Scan).where(Scan.id == self.scan_id)
            )
            scan = result.scalar_one_or_none()
            
            if scan:
                scan.status = ScanStatus.FAILED
                scan.completed_at = datetime.utcnow()
                await self.db.commit()
                logger.info(f"Marked scan {self.scan_id} as failed")
        except Exception as e:
            logger.error(f"Failed to update scan status: {e}")
