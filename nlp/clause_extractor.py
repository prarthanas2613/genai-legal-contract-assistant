import re


def extract_clauses(text):
    """
    Splits contract text into clauses using:
    - Clause numbers (1., 1.1, 2.3 etc.)
    - Headings like 'Clause', 'Section'
    - Paragraph fallback
    """

    # Clean text
    text = re.sub(r'\n+', '\n', text)
    text = text.strip()

    # Pattern for numbered clauses
    clause_pattern = r'(?:\n|^)(?:Clause\s+\d+|\d+\.\d+|\d+)\s*[–\-.:]?\s*'

    splits = re.split(clause_pattern, text)

    clauses = []

    for part in splits:
        part = part.strip()
        if len(part) > 60:  # ignore very small chunks
            clauses.append(part)

    # Fallback: paragraph split if no clauses found
    if not clauses:
        paragraphs = text.split("\n")
        clauses = [p.strip() for p in paragraphs if len(p.strip()) > 80]

    return clauses
