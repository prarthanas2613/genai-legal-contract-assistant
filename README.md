#  GenAI Legal Contract Assistant for Indian SMEs
An AI-powered legal contract analysis platform designed to help Indian small and medium business owners (SMEs) understand complex legal contracts — without needing a lawyer for every document.

## Features

-  Upload contracts in PDF, DOCX, or TXT format
-  Automatic contract type detection (Employment, Service, Vendor, Lease, Partnership)
-  Intelligent clause extraction using heading-based and numbered splitting
-  Risk detection with severity levels (High / Medium / Low)
-  Jurisdiction detection with foreign jurisdiction warnings
-  AI-powered SME advice for each clause:
  - Plain-English explanation of what you're agreeing to
  - Why it's risky for an Indian SME
  - SME-friendly alternative clause
  - Relevant Indian legal context (Indian Contract Act, MSME Act, IT Act etc.)
-  Weighted overall risk score dashboard
-  Downloadable PDF report
-  Audit log for all analyzed contracts

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| NLP | spaCy (en_core_web_sm) |
| Clause Extraction | Custom regex + heading-based parser |
| Risk Detection | Rule-based engine (risk_engine.py) |
| AI Advice | Groq API (llama-3.3-70b-versatile) — Free |
| PDF Export | FPDF2 |
| File Reading | PyMuPDF (PDF), python-docx (DOCX) |
| Translation | deep-translator (Hindi → English) |
| Language Detection | langdetect |

## Project Structure

```
legal-genai-assistant/
├── llm/
│   ├── hf_analyzer.py       # Groq API integration + parsers
│   └── prompts.py           # Prompt templates for clause analysis
├── nlp/
│   ├── clause_extractor.py  # Splits contract into individual clauses
│   ├── contract_classifier.py # Detects contract type
│   └── ner_extractor.py     # Extracts parties, jurisdiction, financials
├── risk/
│   └── risk_engine.py       # Rule-based risk detection engine
├── utils/
│   ├── fonts/               # DejaVuSans font for PDF Unicode support
│   ├── file_reader.py       # Reads PDF, DOCX, TXT files
│   └── pdf_exporter.py      # Generates structured PDF report
├── audit_logs/              # JSON audit trail of all analyses
├── app.py                   # Main Streamlit application
├── .env                     # API keys (not committed to git)
├── requirements.txt         # Python dependencies
└── README.md
```

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/legal-genai-assistant.git
cd legal-genai-assistant
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Set up API keys
Create a `.env` file in the root folder:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```
Get your free Groq API key at: https://console.groq.com

### 5. Run the app
```bash
streamlit run app.py
```

## Risk Scoring

| Severity | Points |
|---|---|
| High | 25 pts per clause |
| Medium | 12 pts per clause |
| Low | 4 pts per clause |

- **70–100%** → High Risk Contract
- **35–69%** → Medium Risk Contract
- **0–34%** → Low Risk Contract

## Disclaimer

This tool is designed to assist Indian SMEs in understanding legal contracts. It is not a substitute for professional legal advice from a qualified advocate. Always consult a lawyer before signing any contract.