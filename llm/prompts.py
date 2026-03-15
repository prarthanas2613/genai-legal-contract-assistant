def clause_prompt(clause, detected_risks=None, jurisdiction=None):
    """
    Generates a structured prompt for the LLM to analyze a legal clause.
    Incorporates specific detected risk tags for better reasoning.
    Returns JSON-parseable output for reliable extraction.
    """
    risk_context = ""
    if detected_risks:
        risk_context = f"Our automated system flagged the following issues: {', '.join(detected_risks)}."

    jurisdiction_context = jurisdiction if jurisdiction else "as specified in the contract"

    return f"""
    You are an expert Legal Counsel specialized in protecting Indian SMEs.
    Analyze the following contract clause and provide a strategic breakdown.

    CLAUSE: "{clause}"
    {risk_context}
    JURISDICTION NOTED IN CONTRACT: {jurisdiction_context}

    You MUST respond with ONLY a valid JSON object. No preamble, no explanation outside the JSON.
    Use this exact structure:

    {{
      "meaning": "Plain-English explanation of what the business owner is agreeing to. No legalese.",
      "why_risky": "Specific dangers this clause poses to an Indian SME. Be concrete — e.g., 'Unlimited liability can lead to personal bankruptcy' or 'London jurisdiction makes litigation financially impossible for most Indian SMEs'.",
      "sme_alternative": "A rewritten 'fair version' of this clause using Indian industry norms. Example: cap liability at 1x contract value, require 30-day notice for termination, limit non-compete to 12 months within India only.",
      "indian_legal_context": "Relevant Indian laws. Examples: Section 27 of Indian Contract Act for non-compete, MSME Development Act for payment terms, IT Act for data clauses. If none apply, state 'No specific Indian statute applies; general contract law governs.'",
      "severity": "High | Medium | Low",
      "negotiable": true
    }}

    Rules:
    - severity must be exactly one of: High, Medium, Low
    - negotiable must be true or false (boolean)
    - All string values must be in plain English, under 120 words each
    - Do NOT include markdown, backticks, or any text outside the JSON object
    """


def jurisdiction_extraction_prompt(contract_text):
    """
    Dedicated prompt to extract jurisdiction from contract text.
    Fixes the bug where jurisdiction defaulted to user's location (India)
    instead of the contract's stated jurisdiction (e.g., London).
    """
    return f"""
    You are a legal document parser. Extract ONLY the jurisdiction/governing law information from this contract.

    CONTRACT TEXT:
    {contract_text[:3000]}

    Respond with ONLY a valid JSON object:
    {{
      "jurisdiction": "The exact jurisdiction stated in the contract (e.g., 'London, United Kingdom', 'Delhi, India')",
      "governing_law": "The governing law stated (e.g., 'Laws of England and Wales', 'Laws of India')",
      "is_foreign_jurisdiction": true,
      "foreign_jurisdiction_risk": "Brief note on what this means for an Indian SME, or null if Indian jurisdiction"
    }}

    If no jurisdiction is mentioned, set jurisdiction to "Not specified" and is_foreign_jurisdiction to false.
    Respond with ONLY the JSON. No other text.
    """


def risk_score_prompt(clauses_summary):
    """
    Calculates overall contract risk score correctly.
    Fixes the flat 50% score bug — weights High clauses more heavily.
    """
    return f"""
    You are a contract risk analyst. Given this summary of clause severities, calculate an overall risk score.

    CLAUSES: {clauses_summary}

    Scoring weights:
    - High severity = 25 points each
    - Medium severity = 12 points each
    - Low severity = 4 points each
    - Maximum score is capped at 100

    Respond with ONLY a valid JSON object:
    {{
      "overall_score": 75,
      "risk_label": "High Risk | Medium Risk | Low Risk",
      "summary": "One sentence explaining the score for a business owner"
    }}

    risk_label rules:
    - 70-100 → "High Risk"
    - 35-69  → "Medium Risk"
    - 0-34   → "Low Risk"

    Respond with ONLY the JSON. No other text.
    """