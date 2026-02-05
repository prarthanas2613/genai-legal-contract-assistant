def clause_prompt(clause):
    return f"""
    You are an expert legal assistant for Indian SMEs. 
    Analyze the following contract clause:
    
    Clause: "{clause}"
    
    Provide the following in simple business English:
    1. MEANING: What does this clause actually mean for a business owner?
    2. RISK: Why is this risky? (Mention high/medium/low risk).
    3. SME ALTERNATIVE: Suggest a fairer, SME-friendly version of this clause.
    4. COMPLIANCE: Note if this follows standard Indian legal norms.
    """