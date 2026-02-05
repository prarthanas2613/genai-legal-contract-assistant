# Place this in nlp/ner_extractor.py
import spacy
from spacy.pipeline import EntityRuler

def extract_legal_entities(text, nlp):
    # Add custom legal patterns if not already present in the pipeline
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": "JURISDICTION", "pattern": [{"LOWER": "jurisdiction"}, {"LOWER": "of"}, {"POS": "PROPN"}]},
            {"label": "AMOUNT", "pattern": [{"TEXT": {"REGEX": "(?i)INR|Rs|Rupees"}}, {"IS_DIGIT": True}]}
        ]
        ruler.add_patterns(patterns)
    
    doc = nlp(text[:10000])
    return {
        "Parties": list(set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]])),
        "Jurisdiction": list(set([ent.text for ent in doc.ents if ent.label_ == "JURISDICTION"])),
        "Financials": list(set([ent.text for ent in doc.ents if ent.label_ == "AMOUNT"]))
    }