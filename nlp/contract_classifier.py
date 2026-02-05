def classify_contract(text):
    text = text.lower()

    categories = {
        "Employment Agreement": [
            "employee", "employer", "salary", "wages",
            "termination of employment", "notice period",
            "job role", "appointment", "probation"
        ],
        "Vendor / Supplier Contract": [
            "vendor", "supplier", "purchase order",
            "supply of goods", "delivery", "invoice",
            "payment terms"
        ],
        "Service Agreement": [
            "services", "scope of work", "service provider",
            "service recipient", "sla", "deliverables"
        ],
        "Lease / Rental Agreement": [
            "lease", "rent", "tenant", "landlord",
            "security deposit", "premises", "monthly rent"
        ],
        "Partnership Deed": [
            "partner", "partnership", "profit sharing",
            "capital contribution", "firm", "dissolution"
        ]
    }

    scores = {}

    for contract_type, keywords in categories.items():
        score = sum(1 for word in keywords if word in text)
        scores[contract_type] = score

    best_match = max(scores, key=scores.get)

    if scores[best_match] == 0:
        return "General Business Contract"

    return best_match
