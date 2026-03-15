# risk/risk_engine.py

HIGH_RISK_TRIGGERS = ["unlimited", "indemnity", "penalty", "sole discretion", "london", "uk"]

def detect_risk(clause: str):
    """
    Detects risks in a clause and returns (risk_level, risks_list).
    Risk level: High / Medium / Low
    Fixed: Medium risk now also returns flagged issues (not empty list).
    """
    clause_lower = clause.lower()
    risks = []

    # ── Specific risk detection ──────────────────────────────────────────────
    if any(w in clause_lower for w in ["penalty", "liquidated damages"]):
        risks.append("Penalty Clause")

    if any(w in clause_lower for w in ["indemnify", "indemnity", "unlimited indemnity"]):
        risks.append("Indemnity Risk")

    if any(w in clause_lower for w in ["terminate at any time", "unilateral", "sole discretion"]):
        risks.append("Unilateral Termination")

    if "non-compete" in clause_lower or "not work with any competitor" in clause_lower:
        risks.append("Non-Compete Risk")

    if any(w in clause_lower for w in ["exclusive jurisdiction", "arbitration", "courts of", "courts in"]):
        risks.append("Jurisdiction / Arbitration Risk")

    if "auto-renewal" in clause_lower or "lock-in" in clause_lower:
        risks.append("Auto-Renewal / Lock-in Risk")

    if any(w in clause_lower for w in ["waives all", "irrevocably waives", "moral rights", "ip waiver"]):
        risks.append("IP / Moral Rights Waiver")

    if "100%" in clause_lower and any(w in clause_lower for w in ["cost", "fees", "arbitration"]):
        risks.append("Unequal Cost Burden")

    if any(w in clause_lower for w in ["5 years", "five years", "globally", "global non-compete"]):
        risks.append("Overbroad Restriction")

    # ── Severity assignment (weighted) ──────────────────────────────────────
    # FIX: was only checking "unlimited" and "penalty" as critical triggers
    # Now also treats indemnity + unilateral together as critical
    is_critical = (
        any(w in clause_lower for w in ["unlimited", "penalty", "irrevocably waives"]) or
        ("indemnity" in clause_lower and "unilateral" in clause_lower)
    )

    if is_critical or len(risks) >= 2:
        risk_level = "High"
    elif len(risks) == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return risk_level, risks