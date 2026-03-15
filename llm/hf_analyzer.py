import json
import re
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_GROQ_KEY = os.getenv("GROQ_API_KEY")
if not _GROQ_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

_client = Groq(api_key=_GROQ_KEY)
_MODEL  = "llama-3.3-70b-versatile"
print("[hf_analyzer] Using Groq API (free)")


def explain_clause(clause: str, detected_risks=None, jurisdiction=None) -> dict:
    from llm.prompts import clause_prompt
    prompt = clause_prompt(clause, detected_risks, jurisdiction)
    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.2
        )
        return parse_clause_analysis(response.choices[0].message.content)
    except Exception as e:
        print(f"[Groq error] {e}")
        return _fallback_result()


def get_jurisdiction(contract_text: str) -> dict:
    patterns = [
        r'exclusive jurisdiction of the courts in ([A-Za-z ,]+?)(?:\.|,|\n)',
        r'courts? in ([A-Za-z ,]+?)(?:\.|,|\n)',
        r'courts? of ([A-Za-z ,]+?)(?:\.|,|\n)',
        r'jurisdiction of ([A-Za-z ,]+?)(?:\.|,|\n)',
        r'governed by the laws of ([A-Za-z ,]+?)(?:\.|,|\n)',
        r'under the laws of ([A-Za-z ,]+?)(?:\.|,|\n)',
    ]
    for pattern in patterns:
        match = re.search(pattern, contract_text, re.IGNORECASE)
        if match:
            jurisdiction = match.group(1).strip().rstrip(",. ")
            is_foreign = not any(
                w in jurisdiction.lower()
                for w in ["india", "delhi", "mumbai", "bangalore", "chennai", "kolkata"]
            )
            return {
                "jurisdiction": jurisdiction,
                "governing_law": jurisdiction,
                "is_foreign_jurisdiction": is_foreign,
                "foreign_jurisdiction_risk": (
                    f"Disputes must be resolved in {jurisdiction}. "
                    "This makes litigation extremely expensive and impractical for Indian SMEs."
                    if is_foreign else None
                ),
            }
    return _fallback_jurisdiction()


def parse_clause_analysis(llm_response: str) -> dict:
    cleaned = re.sub(r"```json|```", "", llm_response).strip()
    result = None
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    if result is None:
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                pass
    if result is None:
        return _fallback_result()
    severity = result.get("severity", "Medium")
    result["severity"] = severity.capitalize() if severity.lower() in ["high", "medium", "low"] else "Medium"
    result["negotiable"] = bool(result.get("negotiable", True))
    result.setdefault("meaning",              "Not available.")
    result.setdefault("why_risky",            "Not available.")
    result.setdefault("sme_alternative",      "Not available.")
    result.setdefault("indian_legal_context", "Not available.")
    return result


def compute_risk_score_locally(clauses: list) -> dict:
    weights = {"high": 25, "medium": 12, "low": 4}
    total   = sum(weights.get(c.get("severity", "low").lower(), 4) for c in clauses)
    score   = min(100, total)
    label   = "High Risk" if score >= 70 else "Medium Risk" if score >= 35 else "Low Risk"
    return {
        "overall_score": score,
        "risk_label":    label,
        "summary":       f"Contract scored {score}/100 across {len(clauses)} clause(s).",
    }


def _fallback_result() -> dict:
    return {
        "meaning":              "Could not analyze clause. Manual review recommended.",
        "why_risky":            "Manual review recommended.",
        "sme_alternative":      "Consult a legal professional for a fair alternative.",
        "indian_legal_context": "Not analyzed.",
        "severity":             "High",
        "negotiable":           True,
    }

def _fallback_jurisdiction() -> dict:
    return {
        "jurisdiction":              "Not specified",
        "governing_law":             "Not specified",
        "is_foreign_jurisdiction":   False,
        "foreign_jurisdiction_risk": None,
    }
