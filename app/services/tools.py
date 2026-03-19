import re
from typing import Dict, Any, List

ICD10_RE = re.compile(r"\b([A-TV-Z][0-9]{2}(?:\.[A-Z0-9]{1,4})?)\b")  # simple ICD-10 matcher
CPT_RE = re.compile(r"\b(\d{5})(?:-([A-Z0-9]{2}))?\b")  # CPT + optional one modifier

E_M_RANGE = list(range(99201, 99500))
PROC_EKG = {93000, 93005, 93010}


def dedupe(seq: List[str]) -> List[str]:
    out, seen = [], set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def analyze_billing_text(text: str, context: str = "") -> Dict[str, Any]:
    icds = [m.group(1) for m in ICD10_RE.finditer(text)]
    cpts = [m.group(1) for m in CPT_RE.finditer(text)]
    mods = [m.group(2) for m in CPT_RE.finditer(text) if m.group(2)]

    icds = dedupe(icds)
    cpts = dedupe(cpts)
    mods = dedupe(mods)

    flags: List[str] = []
    suggestions: List[str] = []

    # Basic heuristic flags
    # 1) No diagnoses found when CPT present
    if cpts and not icds:
        flags.append("CPT codes present but no ICD-10 diagnosis codes detected.")
        suggestions.append("Add at least one ICD-10 diagnosis that supports medical necessity.")

    # 2) E/M with procedure may need -25 (very simplified heuristic)
    em_codes = [int(c) for c in cpts if c.isdigit() and int(c) in E_M_RANGE]
    proc_codes = [int(c) for c in cpts if c.isdigit() and int(c) not in E_M_RANGE]
    if em_codes and proc_codes and not any(m in {"25"} for m in mods):
        flags.append("E/M code with a procedure detected without modifier -25.")
        suggestions.append("If appropriate, append modifier -25 to the E/M service for significant, separately identifiable work.")

    # 3) EKG specific pairing example
    if any(pc in PROC_EKG for pc in proc_codes) and not any(mod in {"59"} for mod in mods):
        suggestions.append("If EKG was distinct from E/M, consider modifier -59 as payer policy allows.")

    # 4) Quantity anomalies (very naive): flag more than 10 occurrences of same CPT in text
    for c in cpts:
        count = len(re.findall(rf"\b{re.escape(c)}\b", text))
        if count > 10:
            flags.append(f"High repeated count for CPT {c} ({count}x). Verify units/quantity.")

    details: Dict[str, Any] = {
        "counts": {
            "icd10": len(icds),
            "cpt": len(cpts),
            "modifiers": len(mods),
        },
        "em_codes": em_codes,
        "procedure_codes": proc_codes,
        "context_excerpt": (context or "")[:400],
    }

    return {
        "icd10_codes": icds,
        "cpt_codes": cpts,
        "modifiers": mods,
        "flags": flags,
        "suggestions": suggestions,
        "details": details,
    }
