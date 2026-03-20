from dataclasses import dataclass

@dataclass
class SourceMeta:
    source_name: str         # "DBHDD" | "CDC" | "CMS/NCHS"
    jurisdiction: str        # "GA" | "US"
    policy_domain: str       # "behavioral_health/ops" | "ipc" | "coding_dx"
    effective_date: str      # "2025-10-01" or ""
    link: str                # canonical URL

    def as_dict(self):
        return {
            "source_name": self.source_name,
            "jurisdiction": self.jurisdiction,
            "policy_domain": self.policy_domain,
            "effective_date": self.effective_date,
            "link": self.link,
        }
