# app/audits/helpers.py

import os
import json
import time
from typing import Dict, Any, List
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters


def _policy_check_snippets(index, question: str, max_snippets: int = 3, sources: List[str] | None = None):
    """Returns up to 3 policy-supporting snippets, preferring DBHDD/CDC/CMS if no sources given."""
    wanted_sources = sources or ["DBHDD", "CDC", "CMS/NCHS"]  # Prefer these sources by default
    filter_kwargs = _build_metadata_filters(policy_only=True, sources=wanted_sources)
    qe = index.as_query_engine(similarity_top_k=6, **filter_kwargs)
    resp = qe.query(question)
    items = []
    for n in getattr(resp, "source_nodes", [])[:max_snippets]:
        node = getattr(n, "node", None)
        if not node:
            continue
        meta = getattr(node, "metadata", {}) or {}
        content = node.get_content()[:600] if hasattr(node, "get_content") else ""
        items.append({
            "snippet": content,
            "source": meta.get("source_name", ""),
            "jurisdiction": meta.get("jurisdiction", ""),
            "policy_domain": meta.get("policy_domain", ""),
            "effective_date": meta.get("effective_date", ""),
            "link": meta.get("link", ""),
        })
    return items

def _build_metadata_filters(policy_only: bool, sources: List[str] | None) -> Dict[str, Any]:
    filters = []
    if policy_only:
        filters.append(MetadataFilter(key="policy_domain", value="behavioral_health/ops"))
    if sources:
        for s in sources:
            filters.append(MetadataFilter(key="source_name", value=s))
    if not filters:
        return {}
    return {"filters": MetadataFilters(filters=filters)}

def _summarize_policy_support(policy_support: List[dict]) -> str:
    """
    Create a concise, human-readable summary of policy requirements
    based on retrieved policy support snippets.
    """
    if not policy_support:
        return "No specific policy excerpts were identified for this scenario."

    bullets = []
    for item in policy_support:
        text = item.get("snippet", "").lower()
        if "discharge summary" in text:
            bullets.append("Completion of a discharge summary documenting services provided, outcomes, referrals, and discharge disposition.")
        if "transition" in text or "discharge/transit" in text:
            bullets.append("Documentation of discharge or transition planning, including follow-up and continuity of care.")
        if "progress notes" in text:
            bullets.append("Maintenance of progress notes reflecting services delivered and client participation.")
        if "signature" in text:
            bullets.append("Documentation of client and/or guardian participation and required signatures when applicable.")

    if not bullets:
        return "DBHDD policy requires appropriate documentation at discharge, including summaries and supporting records."

    # Deduplicate while preserving order
    bullets = list(dict.fromkeys(bullets))

    header = "DBHDD Discharge Documentation Requirements:"
    formatted = ["• " + b for b in bullets]

    return header + "\n" + "\n".join(formatted)

def _identify_policy_gaps(policy_support: List[dict], clinical_text: str) -> List[str]:
    """
    Identify potential documentation gaps by comparing policy requirements
    with the provided clinical text.
    """
    text = clinical_text.lower()
    gaps = []

    if any("discharge summary" in ps.get("snippet", "").lower() for ps in policy_support):
        if "discharge summary" not in text:
            gaps.append("Discharge summary not explicitly documented.")

    if any("transition" in ps.get("snippet", "").lower() for ps in policy_support):
        if "follow-up" not in text and "aftercare" not in text and "transition" not in text:
            gaps.append("Discharge or transition planning documentation is missing or unclear.")

    if any("progress notes" in ps.get("snippet", "").lower() for ps in policy_support):
        if "progress note" not in text:
            gaps.append("Progress notes supporting services at discharge are not mentioned.")

    if any("signature" in ps.get("snippet", "").lower() for ps in policy_support):
        if "signature" not in text:
            gaps.append("Client and/or guardian participation and required signatures are not documented.")

    return gaps
