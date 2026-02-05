from fpdf import FPDF
from datetime import datetime
import os
import re


# ---------------- Text Cleaning ----------------
def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove problematic unicode & artifacts
    text = text.replace("\u00a0", " ")   # non-breaking space
    text = text.replace("…", "...")

    # Fix long underscore/dot placeholders
    text = re.sub(r"[_]{5,}", " _____ ", text)
    text = re.sub(r"[.]{5,}", " ..... ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------- Safe MultiCell ----------------
def safe_multicell(pdf, text, line_height=6):
    """
    Prevents FPDF crash on long tokens / placeholders
    """
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(line_height)
        else:
            pdf.multi_cell(0, line_height, line)


# ---------------- PDF Generator ----------------
def generate_pdf(
    contract_type,
    clauses,
    risk_labels,
    filename,
    issues_list=None,
    explanations=None
):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ---- Load Unicode Font ----
    font_path = os.path.join("utils", "fonts", "DejaVuSans.ttf")

    if not os.path.exists(font_path):
        raise FileNotFoundError(
            "DejaVuSans.ttf not found. Place it inside utils/fonts/"
        )

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_font("DejaVu", "B", font_path, uni=True)
    pdf.add_font("DejaVu", "I", font_path, uni=True)

    # ---- Title ----
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 12, "GenAI Legal Contract Risk Report", ln=True)

    pdf.set_font("DejaVu", size=10)
    pdf.cell(
        0,
        8,
        f"Generated on: {datetime.now().strftime('%d %b %Y')}",
        ln=True
    )
    pdf.ln(5)

    # ---- Contract Overview ----
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Contract Overview", ln=True)

    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 8, f"Contract Type: {contract_type}", ln=True)
    pdf.cell(0, 8, f"Clauses Analyzed: {len(clauses)}", ln=True)

    high_risk = risk_labels.count("High")
    pdf.cell(0, 8, f"High Risk Clauses: {high_risk}", ln=True)
    pdf.ln(5)

    # ---- Clause Analysis ----
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Clause Risk Analysis", ln=True)

    for i, clause in enumerate(clauses):
        # Clause Header
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(
            0,
            8,
            f"Clause {i + 1} – {risk_labels[i]} RISK",
            ln=True
        )

        # Clause Text
        pdf.set_font("DejaVu", size=9)
        safe_multicell(pdf, clean_text(clause))

        # Issues (High Risk only)
        if (
            risk_labels[i] == "High"
            and issues_list
            and i < len(issues_list)
            and issues_list[i]
        ):
            pdf.set_font("DejaVu", "I", 9)
            safe_multicell(
                pdf,
                clean_text("Issues: " + ", ".join(issues_list[i]))
            )

        # AI Explanation
        if explanations and i < len(explanations) and explanations[i]:
            pdf.set_font("DejaVu", size=9)
            safe_multicell(
                pdf,
                clean_text("AI Explanation: " + explanations[i])
            )

        pdf.ln(4)

    # ---- Disclaimer ----
    pdf.ln(5)
    pdf.set_font("DejaVu", "I", 8)
    safe_multicell(
        pdf,
        "Disclaimer: This AI-generated report is for informational "
        "purposes only and does not constitute legal advice."
    )

    # ---- Save PDF ----
    pdf.output(filename)
    return filename
