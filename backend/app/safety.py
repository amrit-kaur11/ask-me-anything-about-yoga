from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class SafetyResult:
    is_unsafe: bool
    reasons: List[str]
    severities: str # "low" | "medium" | "high"

# -------------------------------
# Medical / Safety risk patterns
# -------------------------------
_UNSAFE_PATTERNS: List[Tuple[str, str, str]] = [
# High-risk medical conditions
(r"\bcancer\b|\btumou?r\b|\bchemotherapy\b|\bradiation\b", "Cancer or oncology treatment", "high"),
(r"\bheart condition\b|\bcardiac\b|\barrhythmia\b|\bheart disease\b", "Cardiac condition", "high"),


# Pregnancy-related
(r"\bpregnan(t|cy)\b|\btrimester\b|\bpostpartum\b", "Pregnancy / postpartum", "high"),


# Blood pressure & metabolic
(r"\bhigh blood pressure\b|\bhypertension\b|\bhigh bp\b|\bblood pressure\b", "Blood pressure condition", "medium"),
(r"\bdiabetes\b|\bblood sugar\b", "Diabetes / blood sugar condition", "medium"),


# Neurological / eye
(r"\bglaucoma\b|\bretina\b|\beye pressure\b", "Eye condition (e.g., glaucoma)", "medium"),


# Surgery / injuries
(r"\brecent surgery\b|\bsurgery\b|\bpost[- ]?op\b|\bstitches\b", "Recent surgery / post-op", "high"),
(r"\bhernia\b|\bslipped disc\b|\bherniated\b|\bsciatica\b", "Back/spine condition", "medium"),
(r"\bfracture\b|\bbroken\b|\btear\b|\btorn\b", "Acute injury (fracture/tear)", "high"),


# Concerning symptoms
(r"\bsevere pain\b|\bsharp pain\b|\bnumbness\b|\btingling\b|\bdizziness\b|\bfaint\b", "Concerning symptoms", "high"),
]


# -------------------------------
# Safety detection
# -------------------------------

def check_safety(query: str) -> SafetyResult:
    q = (query or "").strip().lower()
    reasons: List[str] = []
    severities: List[str] = []

    for pattern, reason, severity in _UNSAFE_PATTERNS:
        if re.search(pattern, q, flags=re.IGNORECASE):
            reasons.append(reason)
            severities.append(severity)

    overall_severities = "low"
    if "high" in severities:
        overall_severities = "high"
    elif "medium" in severities:
        overall_severities = "medium"        
    return SafetyResult(is_unsafe=len(reasons) > 0, reasons=reasons, severities=overall_severities)


# -------------------------------
# High-quality safety messaging
# -------------------------------

def unsafe_response_text(result: SafetyResult) -> str:
    """
    This text is appended or injected when safety is triggered.
    It is intentionally empathetic, non-alarmist, and medically responsible.
    """

    reason_line = ""
    if result.reasons:
        reasons_line = (
            "I noticed that your question may relate to the following medical consideration(s): "
            + ", ".join(result.reasons)
            + "."
        )

    doctor_line = (
        "It’s important to consult a qualified healthcare professional or a certified yoga therapist "
        "before starting or modifying any practice."
    )    

    return (
        "⚠️ **Medical Safety Notice**\n\n"
        "I’m not a medical professional, but I want to make sure your safety comes first.\n\n"
        f"{reasons_line}\n\n"
        "**General, non-medical guidance:**\n"
        "- Prefer gentle, low-intensity practices\n"
        "- Avoid breath retention, forceful breathing, or strain\n"
        "- Use supported or restorative postures\n"
        "- Stop immediately if you feel pain, dizziness, or discomfort\n\n"
        f"{doctor_line}\n\n"
        "If you’d like, I can also help you explore *questions to ask your doctor* or "
        "*gentle wellness options that are commonly considered safe with supervision.*"
    )
