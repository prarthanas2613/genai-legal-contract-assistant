import re

# ── Known legal clause headings ───────────────────────────────────────────────
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


def extract_clauses(text: str) -> list:
    """
    Splits contract text into clauses using 3 strategies.
    Minimum clause length set to 150 chars to avoid tiny fragments.
    """
    # Normalize whitespace
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    # ── Strategy 1: Numbered clauses ─────────────────────────────────────────
    numbered_pattern = r'(?:^|\n)(?:Clause|Section|Article)?\s*\d+(?:\.\d+)*[\s.\-:)]+(?=[A-Z])'
    numbered_splits = re.split(numbered_pattern, text, flags=re.MULTILINE)

    if len(numbered_splits) > 2:
        clauses = [c.strip() for c in numbered_splits if len(c.strip()) > 150]
        if clauses:
            return clauses

    # ── Strategy 2: Heading at START OF LINE only ─────────────────────────────
    # Only match heading when preceded by newline — prevents splitting
    # mid-sentence on words that happen to match a heading name
    escaped = [re.escape(h) for h in sorted(LEGAL_HEADINGS, key=len, reverse=True)]
    heading_pattern = r'(?:^|\n\n)(' + '|'.join(escaped) + r')\n'

    parts = re.split(heading_pattern, text, flags=re.IGNORECASE | re.MULTILINE)

    if len(parts) > 3:
        clauses = []

        # Add preamble before first heading
        preamble = parts[0].strip()
        if len(preamble) > 150:
            clauses.append(preamble)

        # Recombine heading + content
        i = 1
        while i < len(parts) - 1:
            heading = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            combined = f"{heading}\n{content}".strip()
            if len(combined) > 150:
                clauses.append(combined)
            i += 2

        if clauses:
            return clauses

    # ── Strategy 3: Paragraph fallback ───────────────────────────────────────
    paragraphs = re.split(r'\n{2,}', text)
    clauses = [p.strip() for p in paragraphs if len(p.strip()) > 150]

    return clauses if clauses else [text]