import os
import streamlit as st
import json
from datetime import datetime
import spacy
from spacy.pipeline import EntityRuler

# Custom module imports
from utils.file_reader import read_file
from nlp.clause_extractor import extract_clauses
from nlp.contract_classifier import classify_contract
from risk.risk_engine import detect_risk
from utils.pdf_exporter import generate_pdf

# LLM Imports (FLAN-T5)
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------- Streamlit Page Configuration ----------------
st.set_page_config(page_title="GenAI Legal Assistant", layout="wide", initial_sidebar_state="expanded")
st.title("🧠 GenAI Legal Contract Assistant for SMEs")
st.markdown("---")

# ---------------- Resource Loading (Cached) ----------------
@st.cache_resource(show_spinner=False)
def load_resources():
    # Load local FLAN-T5 model for legal reasoning
    MODEL_NAME = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    # Load spaCy and configure specialized Legal EntityRuler
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": "JURISDICTION", "pattern": [{"LOWER": "jurisdiction"}, {"LOWER": "of"}, {"POS": "PROPN"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "courts"}, {"LOWER": "at"}, {"POS": "PROPN"}]},
            {"label": "AMOUNT", "pattern": [{"TEXT": {"REGEX": "(?i)INR|Rs|Rupees|Rs\."}}, {"IS_PUNCT": True, "OP": "?"}, {"IS_DIGIT": True}]},
            {"label": "STATUTE", "pattern": [{"LOWER": "section"}, {"IS_DIGIT": True}, {"LOWER": "of"}, {"LOWER": "the"}, {"POS": "PROPN", "OP": "+"}]}
        ]
        ruler.add_patterns(patterns)
        
    return tokenizer, model, nlp

tokenizer, model, nlp = load_resources()

# ---------------- Logic & Utility Functions ----------------

def save_audit_log(filename, contract_type, risk_score):
    """Fulfills Requirement 6: Maintain JSON-based audit trails."""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "contract_type": contract_type,
        "risk_score": f"{risk_score}%",
        "status": "Analysis Verified"
    }
    log_dir = "audit_logs"
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    log_path = os.path.join(log_dir, "audit_trail.json")
    
    logs = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            try: logs = json.load(f)
            except: logs = []
    logs.append(log_entry)
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=4)

def extract_legal_ner(text):
    """Performs NER for critical dimensions: Parties, Dates, Jurisdiction, Financials."""
    doc = nlp(text[:10000])
    return {
        "Parties": list(set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]])),
        "Dates": list(set([ent.text for ent in doc.ents if ent.label_ == "DATE"])),
        "Jurisdiction": list(set([ent.text for ent in doc.ents if ent.label_ == "JURISDICTION"])),
        "Financials": list(set([ent.text for ent in doc.ents if ent.label_ == "AMOUNT"])),
        "Statutes": list(set([ent.text for ent in doc.ents if ent.label_ == "STATUTE"]))
    }

@st.cache_data(show_spinner=False)
def explain_clause_sme(clause: str) -> str:
    """Provides plain-language meaning and SME-friendly alternative clauses."""
    prompt = (
        f"Context: Indian SME Legal Assistant. \n"
        f"Task: Explain this clause in plain English, identify risks, and suggest an SME-friendly alternative.\n"
        f"Clause: {clause}"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=250, do_sample=True, temperature=0.3)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ---------------- User Interface Flow ----------------

uploaded_file = st.file_uploader("Upload Legal Contract (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    # Handle File Reading & Hindi-to-English Normalization
    with st.spinner("Extracting text and translating if necessary..."):
        contract_text = read_file(uploaded_file)
    
    # 1. Classification & Key Entity Recognition
    contract_type = classify_contract(contract_text)
    entities = extract_legal_ner(contract_text)
    
    st.header("📋 Executive Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Contract Category", contract_type)
    col2.write("**Primary Parties:** " + ", ".join(entities["Parties"][:3]) if entities["Parties"] else "Not Detected")
    col3.write("**Jurisdiction:** " + (entities["Jurisdiction"][0] if entities["Jurisdiction"] else "Standard Indian Jurisdiction"))

    with st.expander("🔍 Detailed Entity Extraction (Dates, Financials, Statutes)"):
        st.write("**Identified Dates:**", ", ".join(entities["Dates"]))
        st.write("**Financial Values:**", ", ".join(entities["Financials"]))
        st.write("**Legal References:**", ", ".join(entities["Statutes"]))

    # 2. Detailed Clause-by-Clause Risk Analysis
    clauses = extract_clauses(contract_text)
    st.header(f"📑 Clause Risk Analysis ({len(clauses)} Segments)")
    
    risk_labels, all_issues, explanations = [], [], []

    for idx, clause in enumerate(clauses[:8]): # Analysis limited to first 8 for demo
        risk_level, risks = detect_risk(clause)
        risk_labels.append(risk_level)
        all_issues.append(risks if risk_level == "High" else [])
        
        with st.expander(f"Clause {idx + 1} | Risk Level: {risk_level}"):
            if risk_level == "High":
                st.error(f"⚠️ Flagged Risk Factors: {', '.join(risks)}")
            else:
                st.success("✅ Standard Clause Structure")
            
            st.write(f"**Text Snippet:** {clause[:450]}...")
            
            if st.button(f"Generate SME Advice & Alternative", key=f"btn_{idx}"):
                with st.spinner("Generating reasoning..."):
                    advice = explain_clause_sme(clause)
                    st.divider()
                    st.markdown(f"**💡 Actionable Advice:** {advice}")
                    explanations.append(advice)
            else:
                explanations.append("")

    # 3. Risk Dashboard & Audit Management
    st.divider()
    high_count = risk_labels.count("High")
    overall_score = int((high_count / max(len(risk_labels), 1)) * 100)
    
    st.subheader("📊 Contract Risk Dashboard")
    st.progress(overall_score)
    st.write(f"Aggregate Risk Score: **{overall_score}%**")

    # 4. Final Export & Persistence
    if st.button("Finalize and Export Report"):
        save_audit_log(uploaded_file.name, contract_type, overall_score)
        pdf_path = generate_pdf(contract_type, clauses[:8], risk_labels, "Risk_Report.pdf", all_issues, explanations)
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Detailed PDF Report",
                data=f,
                file_name=f"Risk_Report_{uploaded_file.name}.pdf",
                mime="application/pdf"
            )
        st.success("✅ Analysis finalized. Audit log saved to `audit_logs/audit_trail.json`.")