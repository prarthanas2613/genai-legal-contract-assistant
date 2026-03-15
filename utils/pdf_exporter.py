# utils/pdf_exporter.py
from fpdf import FPDF
from datetime import datetime
import os
import re


# ── Text Cleaning ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Removes characters that cause FPDF to crash."""
    if not text:
        return ""
    text = text.replace("\u00a0", " ").replace("\u20b9", "Rs.").replace("…", "...")
    text = re.sub(r"[_]{5,}", " _____ ", text)
    text = re.sub(r"[.]{5,}", " ..... ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Safe MultiCell ────────────────────────────────────────────────────────────

def safe_multicell(pdf: FPDF, text: str, line_height: int = 6):
    """Handles long text safely without breaking PDF layout."""
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(line_height)
        else:
            pdf.multi_cell(0, line_height, line)


# ── Explanation Parser ────────────────────────────────────────────────────────

def parse_explanation(explanation) -> dict:
    """
    FIX: explanations are now structured dicts from hf_analyzer.
    Handles both old plain-string format and new dict format gracefully.
    """
    if isinstance(explanation, dict):
        return {
            "meaning":              explanation.get("meaning", ""),
            "why_risky":            explanation.get("why_risky", ""),
            "sme_alternative":      explanation.get("sme_alternative", ""),
            "indian_legal_context": explanation.get("indian_legal_context", ""),
        }

    # Legacy plain-string fallback (old format)
    if isinstance(explanation, str) and explanation.strip():
        # Try to split on known prefixes written by app.py flatten
        parts = {
            "meaning":              "",
            "why_risky":            "",
            "sme_alternative":      explanation,   # put full text as alternative
            "indian_legal_context": "",
        }
        for line in explanation.split("\n"):
            if line.startswith("Meaning:"):
                parts["meaning"] = line.replace("Meaning:", "").strip()
            elif line.startswith("Why Risky:"):
                parts["why_risky"] = line.replace("Why Risky:", "").strip()
            elif line.startswith("SME Alternative:"):
                parts["sme_alternative"] = line.replace("SME Alternative:", "").strip()
            elif line.startswith("Indian Legal Context:"):
                parts["indian_legal_context"] = line.replace("Indian Legal Context:", "").strip()
        return parts

    return {
        "meaning":              "",
        "why_risky":            "",
        "sme_alternative":      "Advice not generated.",
        "indian_legal_context": "",
    }


# ── PDF Generator ─────────────────────────────────────────────────────────────

def generate_pdf(
    contract_type: str,
    clauses: list,
    risk_labels: list,
    filename: str,
    issues_list: list = None,
    explanations: list = None,
    jurisdiction: str = None,
    overall_score: int = None,
    risk_label: str = None,
) -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Font setup ────────────────────────────────────────────────────────────
    font_path = os.path.join("utils", "fonts", "DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "",  font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        pdf.add_font("DejaVu", "I", font_path, uni=True)
        F = "DejaVu"
    else:
        F = "Arial"

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_font(F, "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "GenAI Legal Contract Risk Report", ln=True, align="C")

    pdf.set_font(F, size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%d %b %Y | %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    # ── Executive Summary ─────────────────────────────────────────────────────
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font(F, "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Executive Summary", ln=True, fill=True)

    pdf.set_font(F, size=10)
    pdf.cell(0, 8, f"Detected Contract Type: {contract_type}", ln=True)

    # FIX: Show actual jurisdiction from contract, not hardcoded India
    if jurisdiction:
        pdf.cell(0, 8, f"Jurisdiction: {jurisdiction}", ln=True)

    pdf.cell(0, 8, f"Total Clauses Analyzed: {len(clauses)}", ln=True)

    high_risk_count   = risk_labels.count("High")
    medium_risk_count = risk_labels.count("Medium")

    if high_risk_count > 0:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, f"High Risk Flags Detected: {high_risk_count}", ln=True)
    if medium_risk_count > 0:
        pdf.set_text_color(200, 100, 0)
        pdf.cell(0, 8, f"Medium Risk Flags Detected: {medium_risk_count}", ln=True)
    if high_risk_count == 0 and medium_risk_count == 0:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(0, 8, "No High or Medium Risk Flags Detected.", ln=True)

    # FIX: Show weighted risk score instead of flat 50%
    if overall_score is not None:
        pdf.set_text_color(0, 51, 102)
        label_str = f" ({risk_label})" if risk_label else ""
        pdf.cell(0, 8, f"Overall Risk Score: {overall_score}%{label_str}", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # ── Detailed Clause Analysis ──────────────────────────────────────────────
    pdf.set_font(F, "B", 12)
    pdf.cell(0, 10, "Detailed Clause Breakdown", ln=True)
    pdf.ln(2)

    for i, clause in enumerate(clauses):
        risk = risk_labels[i] if i < len(risk_labels) else "Low"

        # Colour-coded severity header
        if risk == "High":
            pdf.set_fill_color(255, 230, 230)
        elif risk == "Medium":
            pdf.set_fill_color(255, 255, 204)
        else:
            pdf.set_fill_color(230, 255, 230)

        pdf.set_font(F, "B", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, f" Clause {i + 1} | Severity: {risk}", ln=True, fill=True)

        # Original clause text
        pdf.set_font(F, size=9)
        pdf.ln(2)
        safe_multicell(pdf, clean_text(clause))
        pdf.ln(2)

        # Flagged issues
        if issues_list and i < len(issues_list) and issues_list[i]:
            pdf.set_font(F, "B", 9)
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 6, "Flagged Risks:", ln=True)
            pdf.set_font(F, "I", 9)
            pdf.multi_cell(0, 5, "- " + "\n- ".join(issues_list[i]))
            pdf.ln(2)

        # ── FIX: All 4 structured advice fields now appear in PDF ────────────
        if explanations and i < len(explanations) and explanations[i]:
            advice = parse_explanation(explanations[i])

            sections = [
                ("What You're Agreeing To",  advice["meaning"],              (0, 51, 102)),
                ("Why It's Risky",           advice["why_risky"],            (180, 0, 0)),
                ("SME-Friendly Alternative", advice["sme_alternative"],      (0, 100, 0)),
                ("Indian Legal Context",     advice["indian_legal_context"], (100, 60, 0)),
            ]

            for section_title, section_text, colour in sections:
                if section_text and section_text.strip():
                    pdf.set_font(F, "B", 9)
                    pdf.set_text_color(*colour)
                    pdf.cell(0, 6, section_title + ":", ln=True)
                    pdf.set_font(F, "I", 9)
                    pdf.set_text_color(50, 50, 50)
                    safe_multicell(pdf, clean_text(section_text))
                    pdf.ln(2)
        else:
            pdf.set_font(F, "I", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, "SME Mitigation Strategy: Click 'Generate SME Advice' in app to populate.", ln=True)

        pdf.set_text_color(0, 0, 0)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    pdf.set_y(-25)
    pdf.set_font(F, "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(
        0, 4,
        "Disclaimer: This report is generated by an AI assistant for SMEs. "
        "It is not a substitute for professional legal advice from a qualified "
        "advocate. Use this analysis to prepare for legal consultations.",
        align="C"
    )

    pdf.output(filename)
    return filename