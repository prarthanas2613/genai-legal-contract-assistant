from langdetect import detect
from deep_translator import GoogleTranslator

import fitz  # PyMuPDF
import docx


def read_file(file):
    text = ""

    # -------- Read file --------
    if file.name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        text = "\n".join(p.text for p in doc.paragraphs)

    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")

    else:
        return ""

    # -------- Language detection & translation --------
    try:
        lang = detect(text)
        if lang == "hi":
            text = GoogleTranslator(source="hi", target="en").translate(text)
    except:
        pass

    return text
