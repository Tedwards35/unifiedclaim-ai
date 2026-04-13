# app/audits/registry.py

from typing import List
from app.audits.base import AuditModule
from app.audits.dbhdd_discharge import DBHDDDischargeAudit


def get_registered_audits() -> List[AuditModule]:
    """
    Returns all audit modules that should be executed for analysis.
    """
    return [
        DBHDDDischargeAudit(),
    ]
