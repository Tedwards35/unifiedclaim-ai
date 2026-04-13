# app/audits/base.py

from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class AuditResult:
    policy_support: List[Dict[str, Any]]
    policy_summary: str
    policy_gaps: List[str]

class AuditModule:
    """
    Base contract for all audit modules.
    Each audit module must implement this interface.
    """

    name: str = "Base Audit"
    policy_sources: List[str] = []

    def run(self, text: str) -> AuditResult:
        """
        Execute the audit on the provided clinical text.
        Must return an AuditResult.
        """
        raise NotImplementedError("Audit modules must implement run()")
