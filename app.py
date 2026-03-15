import os
import json
import streamlit as st
from datetime import datetime
import spacy

# ---------------- Custom Imports ----------------
from utils.file_reader import read_file
from nlp.clause_extractor import extract_clauses
from nlp.contract_classifier import classify_contract
from risk.risk_engine import detect_risk
from utils.pdf_exporter import generate_pdf

# ---------------- LLM Imports ----------------
from llm.hf_analyzer import explain_clause, get_jurisdiction, compute_risk_score_locally

# ---------------- Streamlit Config ----------------
st.set_page_config(
    page_title="GenAI Legal Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 GenAI Legal Contract Assistant for SMEs")
st.divider()

# ---------------- Colorful Theme CSS ----------------
st.markdown("""
<style>
.main {background: linear-gradient(to bottom right, #f0f4f8, #d9e2ec); color: #102a43;}
.clause-card {padding:20px; border-radius:12px; margin-bottom:15px; border-left:5px solid #6c757d; background-color:#fff; box-shadow:0px 4px 6px rgba(0,0,0,0.1);}
.risk-high { border-left-color: #FF4B4B; background-color: #ffe5e5; }
.risk-medium { border-left-color: #FFA500; background-color: #fff4e5; }
.risk-low { border-left-color: #28A745; background-color: #e5ffe5; }
.stMetric {background-color:#fff; padding:15px; border-radius:10px; box-shadow:0 4px 6px rgba(0,0,0,0.1);}
.stButton>button {border-radius:20px; border:none; background:linear-gradient(90deg, #36d1dc, #5b86e5); color:white; font-weight:bold; transition:all 0.3s ease;}
.stButton>button:hover {background:linear-gradient(90deg, #5b86e5, #36d1dc); transform:scale(1.05);}
h3,h4 {color:#102a43;}
</style>
""", unsafe_allow_html=True)

# ---------------- Load Resources ----------------
@st.cache_resource(show_spinner=False)
def load_nlp():
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns([
            {"label": "JURISDICTION", "pattern": [{"LOWER": "courts"}, {"LOWER": "of"}, {"POS": "PROPN"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "jurisdiction"}, {"LOWER": "of"}, {"POS": "PROPN"}]},
            {"label": "JURISDICTION", "pattern": [{"LOWER": "governed"}, {"LOWER": "by"}, {"LOWER": "the"}, {"LOWER": "laws"}, {"LOWER": "of"}, {"POS": "PROPN"}]},
            {"label": "AMOUNT", "pattern": [{"TEXT": {"REGEX": "(?i)INR|Rs|Rupees"}}, {"IS_DIGIT": True}]},
        ])
    return nlp

# NOTE: tokenizer + model are now loaded inside hf_analyzer.py (no duplication)
nlp = load_nlp()

# ---------------- Utility Functions ----------------
def save_audit_log(filename, contract_type, risk_score):
    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "contract_type": contract_type,
        "risk_score": f"{risk_score}%",
        "status": "Verified"
    }

    os.makedirs("audit_logs", exist_ok=True)
    path = "audit_logs/audit_trail.json"

    data = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []

    data.append(log)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def extract_legal_ner(text):
    doc = nlp(text[:10000])
    return {
        "Parties":      list(set(ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON"])),
        "Dates":        list(set(ent.text for ent in doc.ents if ent.label_ == "DATE")),
        "Jurisdiction": list(set(ent.text for ent in doc.ents if ent.label_ == "JURISDICTION")),
        "Financials":   list(set(ent.text for ent in doc.ents if ent.label_ == "AMOUNT")),
    }


@st.cache_data(show_spinner=False)
def explain_clause_sme(clause: str, risks: list, jurisdiction: str) -> dict:
    """
    Calls hf_analyzer.explain_clause() which now returns a structured dict.
    Cached so the model doesn't re-run on every Streamlit rerender.
    """
    return explain_clause(clause, detected_risks=risks, jurisdiction=jurisdiction)


# ---------------- Session State Init ----------------
for key in ["explanations_map", "contract_text", "clauses", "risk_labels", "all_issues", "jurisdiction"]:
    if key not in st.session_state:
        st.session_state[key] = None

if "explanations_map" not in st.session_state or st.session_state.explanations_map is None:
    st.session_state.explanations_map = {}

# ---------------- UI Flow ----------------
uploaded_file = st.file_uploader(
    "Upload Legal Contract (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file and st.session_state.contract_text is None:
    with st.spinner("Reading contract..."):
        st.session_state.contract_text = read_file(uploaded_file)

if st.session_state.contract_text:
    contract_text = st.session_state.contract_text
    contract_type = classify_contract(contract_text)
    entities      = extract_legal_ner(contract_text)

    # ── FIX 1: Jurisdiction from contract text, not user location ──
    if st.session_state.jurisdiction is None:
        with st.spinner("Detecting jurisdiction..."):
            jurisdiction_data = get_jurisdiction(contract_text)
            st.session_state.jurisdiction = jurisdiction_data.get("jurisdiction", "Not specified")

    jurisdiction_display = st.session_state.jurisdiction

    # ── Executive Summary ──
    st.subheader("📋 Executive Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Contract Type", contract_type)

    with col2:
        parties = entities["Parties"][:3]
        st.write("**Parties:** " + (", ".join(parties) if parties else "Not detected"))

    with col3:
        st.write(f"**Jurisdiction:** {jurisdiction_display}")
        jurisdiction_data = get_jurisdiction(contract_text) if st.session_state.jurisdiction else {}
        if jurisdiction_data.get("is_foreign_jurisdiction"):
            st.warning(f"⚠️ Foreign jurisdiction detected. {jurisdiction_data.get('foreign_jurisdiction_risk', '')}")

    # ── Clause Extraction ──
    if st.session_state.clauses is None:
        st.session_state.clauses = extract_clauses(contract_text)

    clauses = st.session_state.clauses
    st.subheader(f"📑 Clause Risk Analysis ({len(clauses[:15])})")

    # ── Risk Detection ──
    if st.session_state.risk_labels is None or st.session_state.all_issues is None:
        st.session_state.risk_labels = []
        st.session_state.all_issues  = []
        for clause in clauses[:15]:
            risk_level, risks = detect_risk(clause)
            st.session_state.risk_labels.append(risk_level)
            st.session_state.all_issues.append(risks)

    risk_labels        = st.session_state.risk_labels
    all_issues         = st.session_state.all_issues
    explanations_for_pdf = []

    for idx, clause in enumerate(clauses[:15]):
        risk_level = risk_labels[idx]
        risks      = all_issues[idx]
        advice_key = f"advice_{idx}"

        st.markdown(f"### Clause {idx + 1} — **{risk_level} Risk**")
        st.caption(clause[:600])

        # ── FIX 2: Medium AND High both show risk flags (not "Standard clause") ──
        if risk_level in ("High", "Medium"):
            if risks:
                if risk_level == "High":
                    st.error(f"⚠️ Issues: {', '.join(risks)}")
                else:
                    st.warning(f"⚠️ Issues: {', '.join(risks)}")
            else:
                st.warning("⚠️ Medium risk detected — review recommended.")
        else:
            st.success("✅ Low risk clause")

        # ── Generate AI Advice ──
        if advice_key not in st.session_state.explanations_map:
            st.session_state.explanations_map[advice_key] = None

        if st.button("Generate SME Advice", key=f"btn_{idx}"):
            if st.session_state.explanations_map[advice_key] is None:
                with st.spinner("Generating AI explanation..."):
                    # ── FIX 3: explain_clause now returns a dict, not a string ──
                    st.session_state.explanations_map[advice_key] = explain_clause_sme(
                        clause, risks, jurisdiction_display
                    )

        advice = st.session_state.explanations_map.get(advice_key)

        if advice and isinstance(advice, dict):
            # Display all 4 structured fields
            with st.expander("📖 Full SME Analysis", expanded=True):
                st.markdown("**📌 What You're Agreeing To**")
                st.info(advice.get("meaning", "Not available."))

                st.markdown("**⚠️ Why It's Risky**")
                st.error(advice.get("why_risky", "Not available."))

                st.markdown("**✅ SME-Friendly Alternative**")
                st.success(advice.get("sme_alternative", "Not available."))

                st.markdown("**⚖️ Indian Legal Context**")
                st.warning(advice.get("indian_legal_context", "Not available."))

                if advice.get("negotiable"):
                    st.caption("🔄 This clause is negotiable.")
                else:
                    st.caption("🔒 This clause may be non-negotiable.")

            # Flatten dict to string for PDF export
            explanations_for_pdf.append(
                f"Meaning: {advice.get('meaning','')}\n"
                f"Why Risky: {advice.get('why_risky','')}\n"
                f"SME Alternative: {advice.get('sme_alternative','')}\n"
                f"Indian Legal Context: {advice.get('indian_legal_context','')}"
            )
        else:
            explanations_for_pdf.append("Advice not generated.")

        st.divider()

    # ── FIX 4: Weighted risk score (not flat High-only count) ──
    clause_dicts = [{"severity": lvl} for lvl in risk_labels]
    score_data   = compute_risk_score_locally(clause_dicts)
    overall_score = score_data["overall_score"]
    risk_label    = score_data["risk_label"]

    st.subheader("📊 Risk Dashboard")
    st.progress(overall_score / 100)
    st.write(f"Overall Risk Score: **{overall_score}%** — {risk_label}")
    st.caption(score_data["summary"])

    # Visual Clause Map
    cols      = st.columns(len(risk_labels))
    color_map = {"High": "#FF4B4B", "Medium": "#FFA500", "Low": "#28A745"}
    for i, status in enumerate(risk_labels):
        cols[i].markdown(f"""
            <div style='text-align:center; background-color:{color_map.get(status,"#6c757d")};
            color:white; border-radius:5px; padding:5px;'>{i+1}</div>
        """, unsafe_allow_html=True)

    # ── Export ──
    if st.button("Finalize & Export PDF"):
        save_audit_log(uploaded_file.name, contract_type, overall_score)
        pdf_path = generate_pdf(
            contract_type,
            clauses[:15],
            risk_labels,
            "Report.pdf",
            all_issues,
            explanations_for_pdf,
            jurisdiction=jurisdiction_display,
            overall_score=overall_score,
            risk_label=risk_label
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download PDF Report",
                data=f,
                file_name=f"Report_{uploaded_file.name}.pdf",
                mime="application/pdf"
            )

        st.success("✅ Report generated and audit log saved.")
