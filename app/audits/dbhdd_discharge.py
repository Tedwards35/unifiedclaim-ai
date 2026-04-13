# app/audits/dbhdd_discharge.py

from typing import List
from app.audits.base import AuditModule, AuditResult
from app.audits.helpers import (
    _policy_check_snippets,
    _summarize_policy_support,
    _identify_policy_gaps,
)
from app.services.rag import get_or_create_index


class DBHDDDischargeAudit(AuditModule):
    """
    Audit module for DBHDD discharge documentation requirements.
    """

    name = "DBHDD Discharge Documentation Audit"
    policy_sources = ["DBHDD"]

    def run(self, text: str) -> AuditResult:
        index = get_or_create_index()

        policy_query = (
            "DBHDD discharge or transition planning documentation requirements, "
            "including discharge summaries, follow-up plans, aftercare, and required records "
            "when services are terminated or transitioned."
        )

        policy_support = _policy_check_snippets(
            index,
            policy_query,
            sources=self.policy_sources,
        )

        policy_summary = _summarize_policy_support(policy_support)
        policy_gaps = _identify_policy_gaps(policy_support, text)

        return AuditResult(
            policy_support=policy_support,
            policy_summary=policy_summary,
            policy_gaps=policy_gaps,
        )
