from langdetect import detect
from deep_translator import GoogleTranslator
import fitz  # PyMuPDF
import docx
import re

# ── Exact legal clause headings (must match whole word at line start only) ────
LEGAL_HEADINGS = [
    "Interpretation", "Position", "Term and Probation Period", "Probation Period",
    "Performance of Duties", "Compensation", "Obligations of the Employee",
    "Leave Policy", "Assignment", "Competing Businesses", "Non-Compete",
    "Confidentiality", "Remedies", "Amendment and Termination", "Termination",
    "Restrictive Covenant", "Notices", "Non-Assignment", "Successors",
    "Indemnification", "Indemnity", "Modification", "Severability",
    "Paragraph Headings", "Applicable Law and Jurisdiction", "Jurisdiction",
    "Counterparts", "Governing Law", "Dispute Resolution", "Arbitration",
    "Intellectual Property", "Force Majeure", "Warranty", "Representations",
    "Liability", "Payment Terms", "Scope of Work", "Deliverables",
    "Confidential Information", "Non-Disclosure", "Non-Solicitation",
    "Background", "Recitals", "Definitions", "General", "Miscellaneous",
]

# Build set for fast lookup
_HEADING_SET = set(h.lower() for h in LEGAL_HEADINGS)


def read_file(file) -> str:
    text = ""

    # ── Read file ─────────────────────────────────────────────────────────────
    if file.name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        paragraphs = []

        for p in doc.paragraphs:
            para_text = p.text.strip()
            if not para_text:
                continue

            # Check if this paragraph IS a heading (exact match or heading style)
            is_exact_heading = para_text.lower() in _HEADING_SET
            is_style_heading = p.style.name.startswith("Heading")

            if is_exact_heading or is_style_heading:
                # Add blank line before and after heading paragraph
                if paragraphs and paragraphs[-1] != "":
                    paragraphs.append("")
                paragraphs.append(para_text)
                paragraphs.append("")
            else:
                paragraphs.append(para_text)

        text = "\n".join(paragraphs)

        # FIX: Insert newline ONLY before headings that appear at the very
        # start of a sentence boundary — after ". " or ") " — NOT inside
        # a word like "confidential information" or "Leave Policy of the..."
        # Pattern: heading appears after sentence-ending punctuation + space
        escaped = [re.escape(h) for h in sorted(LEGAL_HEADINGS, key=len, reverse=True)]
        # Only split after ". " or ".\n" — i.e. end of a sentence
        sentence_boundary = r'(?<=[.!?])\s+(?=' + '|'.join(escaped) + r')'
        text = re.sub(sentence_boundary, '\n\n', text, flags=re.IGNORECASE)

    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")

    else:
        return ""

    # ── Language detection & translation ──────────────────────────────────────
    try:
        lang = detect(text)
        if lang == "hi":
            text = GoogleTranslator(source="hi", target="en").translate(text)
    except Exception:
        pass

    return text