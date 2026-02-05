# GenAI Legal Assistant for Indian SMEs

This project is a GenAI-powered legal contract analysis platform designed to help small and medium business owners understand complex legal contracts.
This project uses only open-source models and does not rely on OpenAI or paid APIs.


## Features
- Contract type classification
- Clause extraction
- Risk detection
- Plain-English explanations using Hugging Face FLAN-T5
- PDF / DOCX / TXT support
- SME-focused legal insights

## Tech Stack
- LLM: Hugging Face FLAN-T5
- NLP: spaCy / custom rule-based extraction
- Backend: Python
- UI: Streamlit
- PDF Generation: ReportLab / FPDF
Uses Hugging Face FLAN-T5 model for clause explanation and summarization. No OpenAI or paid APIs are used.


## How to Run
1. Activate virtual environment
2. Install requirements
3. Run: streamlit run app.py
