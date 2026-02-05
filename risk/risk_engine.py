def detect_risk(clause):
    """
    Detects risk in a single clause.
    Returns:
        risk_level: 'Low', 'Medium', 'High'
        risks: List of flagged issues
    """

    clause_lower = clause.lower()
    risks = []

    # -------- High-risk keywords --------
    if any(word in clause_lower for word in ["penalty", "liquidated damages"]):
        risks.append("Penalty Clause")

    if any(word in clause_lower for word in ["indemnify", "indemnity"]):
        risks.append("Indemnity Risk")

    if "terminate at any time" in clause_lower or "unilateral termination" in clause_lower:
        risks.append("Unilateral Termination")

    if "non-compete" in clause_lower:
        risks.append("Non-Compete Risk")

    if any(word in clause_lower for word in ["exclusive jurisdiction", "arbitration"]):
        risks.append("Jurisdiction / Arbitration Risk")

    if "auto-renewal" in clause_lower or "lock-in period" in clause_lower:
        risks.append("Auto-Renewal / Lock-in Risk")

    # -------- Assign risk level --------
    if len(risks) >= 2:
        risk_level = "High"
    elif len(risks) == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return risk_level, risks
