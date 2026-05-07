from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class VulnerabilityIssue(BaseModel):
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    description: str
    evidence: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None
    location: Optional[str] = None

class ScanContext:
    def __init__(self, target_url: str, session, soup=None):
        self.target_url = target_url
        self.session = session
        self.soup = soup
        # Add more context as needed (e.g. detected tech stacks)

class VulnerabilityCheck(ABC):
    name: str = "Base Check"
    severity: str = "LOW"
    category: str = "General"
    description: str = "Base description"

    @abstractmethod
    async def run(self, context: ScanContext) -> List[VulnerabilityIssue]:
        """
        Run the vulnerability check against the context.
        Returns a list of VulnerabilityIssue findings.
        """
        pass
