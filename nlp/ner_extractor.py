# nlp/ner_extractor.py
import spacy

def extract_legal_entities(text: str, nlp) -> dict:
    """
    Extracts legal entities from contract text.
    FIX: Added more jurisdiction patterns so London/UK is detected correctly
         instead of defaulting to India.
    """
    # Add custom legal patterns if not already in pipeline
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            # "courts in London"
            {"label": "JURISDICTION", "pattern": [
                {"LOWER": "courts"}, {"LOWER": "in"}, {"POS": "PROPN"}
            ]},
            # "courts of London"
            {"label": "JURISDICTION", "pattern": [
                {"LOWER": "courts"}, {"LOWER": "of"}, {"POS": "PROPN"}
            ]},
            # "jurisdiction of London"
            {"label": "JURISDICTION", "pattern": [
                {"LOWER": "jurisdiction"}, {"LOWER": "of"}, {"POS": "PROPN"}
            ]},
            # "exclusive jurisdiction of the courts in London"
            {"label": "JURISDICTION", "pattern": [
                {"LOWER": "exclusive"}, {"LOWER": "jurisdiction"}, {"LOWER": "of"},
                {"LOWER": "the"}, {"LOWER": "courts"}, {"LOWER": "in"}, {"POS": "PROPN"}
            ]},
            # "governed by the laws of England"
            {"label": "JURISDICTION", "pattern": [
                {"LOWER": "governed"}, {"LOWER": "by"}, {"LOWER": "the"},
                {"LOWER": "laws"}, {"LOWER": "of"}, {"POS": "PROPN"}
            ]},
            # "under the laws of United Kingdom"
            {"label": "JURISDICTION", "pattern": [
                {"LOWER": "under"}, {"LOWER": "the"}, {"LOWER": "laws"},
                {"LOWER": "of"}, {"POS": "PROPN"}
            ]},
            # Financial patterns
            {"label": "AMOUNT", "pattern": [
                {"TEXT": {"REGEX": "(?i)INR|Rs\\.?|Rupees?"}}, {"IS_DIGIT": True}
            ]},
        ]
        ruler.add_patterns(patterns)

    doc = nlp(text[:10000])

    # ── Regex fallback for jurisdiction ──────────────────────────────────────
    # spaCy may miss jurisdiction if PROPN tagger fails — regex catches it
    import re
    jurisdiction_regex = re.findall(
        r'(?:courts?\s+(?:in|of)|exclusive jurisdiction of(?:\s+the courts\s+in)?|'
        r'governed by the laws of|under the laws of)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|\n|$)',
        text, re.IGNORECASE
    )
    regex_jurisdictions = [j.strip() for j in jurisdiction_regex if j.strip()]

    spacy_jurisdictions = list(set(
        ent.text for ent in doc.ents if ent.label_ == "JURISDICTION"
    ))

    # Merge both sources, prefer specific matches
    all_jurisdictions = list(set(spacy_jurisdictions + regex_jurisdictions))

    return {
        "Parties":      list(set(ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON"])),
        "Dates":        list(set(ent.text for ent in doc.ents if ent.label_ == "DATE")),
        "Jurisdiction": all_jurisdictions,
        "Financials":   list(set(ent.text for ent in doc.ents if ent.label_ == "AMOUNT")),
    }