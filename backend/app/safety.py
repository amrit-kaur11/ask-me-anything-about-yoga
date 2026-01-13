from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class SafetyResult:
    is_unsafe: bool
    reasons: List[str]


_UNSAFE_PATTERNS: List[Tuple[str, str]] = [
    (r"\bpregnan(t|cy)\b|\btrimester\b|\bpostpartum\b", "Pregnancy / postpartum"),
    (r"\bglaucoma\b|\bretina\b|\beye pressure\b", "Eye condition (e.g., glaucoma)"),
    (r"\bhigh blood pressure\b|\bhypertension\b|\bhigh bp\b|\bblood pressure\b", "Blood pressure condition"),
    (r"\brecent surgery\b|\bsurgery\b|\bpost[- ]?op\b|\bstitches\b", "Recent surgery / post-op"),
    (r"\bhernia\b|\bslipped disc\b|\bherniated\b|\bsciatica\b", "Back/spine condition (e.g., hernia/disc/sciatica)"),
    (r"\bfracture\b|\bbroken\b|\btear\b|\btorn\b", "Acute injury (fracture/tear)"),
    (r"\bsevere pain\b|\bsharp pain\b|\bnumbness\b|\btingling\b|\bdizziness\b", "Concerning symptoms (pain/numbness/dizziness)"),
    (r"\bheart condition\b|\bcardiac\b|\barrhythmia\b", "Cardiac condition"),
]


def check_safety(query: str) -> SafetyResult:
    q = (query or "").strip().lower()
    reasons: List[str] = []
    for pattern, reason in _UNSAFE_PATTERNS:
        if re.search(pattern, q, flags=re.IGNORECASE):
            reasons.append(reason)
    return SafetyResult(is_unsafe=len(reasons) > 0, reasons=reasons)


def unsafe_response_text(reasons: List[str]) -> str:
    reason_line = ""
    if reasons:
        reason_line = "I noticed potential risk factors: " + ", ".join(reasons) + "."

    return (
        "Your question touches on an area that can be risky without personalized guidance.\n\n"
        f"{reason_line}\n\n"
        "Safer alternative (general guidance): consider gentle, low-intensity options such as "
        "supported restorative poses (e.g., props-supported relaxation), seated breathing (without strain), "
        "and slow mobility work—avoiding strong inversions, deep backbends, or intense holds.\n\n"
        "Please consult a doctor and/or a certified yoga therapist before attempting any new poses, "
        "especially if you have medical conditions or are recovering from injury/surgery."
    )
