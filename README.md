# GenAI Legal Assistant for Indian SMEs

GenAI Legal Assistant is a legal contract analysis platform powered by open-source AI models, designed to help small and medium business owners understand complex legal contracts. This project uses only open-source models and does not rely on OpenAI or paid APIs.


## Features
- Contract type classification
- Clause extraction
- Risk detection(High/ Medium/ Low)
- Plain-English explanations using Hugging Face FLAN-T5
- Spport for PDF / DOCX / TXT support
- SME-focused legal insights

## Tech Stack
- LLM: Hugging Face FLAN-T5(for clause explanation and summarization)
- NLP: spaCy + custom rule-based extraction
- Backend: Python
- UI: Streamlit
- PDF Generation: ReportLab / FPDF
Uses Hugging Face FLAN-T5 model for clause explanation and summarization. No OpenAI or paid APIs are used.

## Installation & Running
•	git clone<https://github.com/prarthanas2613/genai-legal-contract-assistant>

•	Activate virtual environment

•	Install: pip install requirements.txt

•	Run: -streamlit run app.py

## How it Works
•	Upload a contract(PDF/DOCX/TXT)

•	Extract contract type and clauss automatically.

•	Detect risky clauses(High/Medium/Low)

•	Generate plain english explanations for each clause using FLAN-T5.

•	Visualize risk dashboard and download a PDF report

## Problem Statement:
Example: “Small and medium-sized enterprises (SMEs) often struggle to review legal contracts due to time and expertise constraints. Manual review is slow and prone to errors.”

## Solution:
Example: “GenAI Legal Contract Assistant automates contract review by extracting clauses, detecting risk levels, and providing AI-generated explanations in plain language. Users can upload contracts and generate a summarized PDF report for quick decision-making.”

## Key Features:

Contract type detection (Employment, NDA, etc.)

Clause risk analysis (High/Medium/Low)

AI advice generation for SMEs

Downloadable PDF report with explanations

Audit log for compliance

## Impact:
Example: “This tool saves SMEs time and reduces legal risk by providing a fast, automated contract review system.”
