# nlp/contract_classifier.py

def classify_contract(text: str) -> str:
    """
    Classifies the contract type based on keyword scoring.
    Returns the best-matched contract category.
    """
    text_lower = text.lower()

    # ── 1. Fast-pass for high-signal keywords ────────────────────────────────
    employment_keywords = ["offer letter", "intern", "stipend", "appointment", "probation"]
    if any(k in text_lower for k in employment_keywords):
        return "Employment Agreement"

    # ── 2. Category keyword scoring ──────────────────────────────────────────
    categories = {
        "Employment Agreement": [
            "employee", "employer", "salary", "wages",
            "termination of employment", "notice period",
            "job role", "appointment", "probation",
        ],
        "Vendor / Supplier Contract": [
            "vendor", "supplier", "purchase order",
            "supply of goods", "delivery", "invoice",
            "payment terms",
        ],
        "Service Agreement": [
            "services", "scope of work", "service provider",
            "service recipient", "sla", "deliverables",
        ],
        "Lease / Rental Agreement": [
            "lease", "rent", "tenant", "landlord",
            "security deposit", "premises", "monthly rent",
        ],
        "Partnership Deed": [
            "partner", "partnership", "profit sharing",
            "capital contribution", "firm", "dissolution",
        ],
    }

    scores = {
        contract_type: sum(1 for word in keywords if word in text_lower)
        for contract_type, keywords in categories.items()
    }

    best_match = max(scores, key=scores.get)

    if scores[best_match] == 0:
        return "General Business Contract"

    return best_match


def get_risk_tag(risk_level: str, risks: list) -> tuple:
    """
    FIX: Returns correct display tag and colour for a clause.
    Previously Medium risk was incorrectly labelled '✅ Standard clause'.

    Returns:
        (tag_text, tag_type)
        tag_type: 'error' | 'warning' | 'success'
    """
    if risk_level == "High":
        tag_text = f"⚠️ Issues: {', '.join(risks)}" if risks else "⚠️ High risk detected"
        return tag_text, "error"

    elif risk_level == "Medium":
        # FIX: Medium is NOT a standard clause — show actual issues
        tag_text = f"⚠️ Issues: {', '.join(risks)}" if risks else "⚠️ Medium risk — review recommended"
        return tag_text, "warning"

    else:
        return "✅ Low risk clause", "success"