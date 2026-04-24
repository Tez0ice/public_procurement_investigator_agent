# 🛡️ KONTRAX AI
### Procurement Integrity Advisor for Malaysian Government Contracts

> **Prototype v1.0** — Shift from reactive corruption detection to **proactive integrity-by-design**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Clause Integrity Checker** | Analyzes draft contract clauses against Malaysian Treasury/MACC/OCDS standards |
| 🔍 **Red-Flag Scanner** | Scans executed contracts for procurement irregularities |
| 🌐 **Bilingual** | Full English / Bahasa Malaysia support |
| 📊 **Risk Scoring** | Color-coded risk meter with explainable triggers |
| 📋 **Audit Trail** | Session-based log of all analyses and user feedback |
| 📄 **Export** | Download Markdown reports for offline review |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Google Gemini API key (free tier available at [aistudio.google.com](https://aistudio.google.com))

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
```

### 4. Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
integritikontrak/
├── app.py                          # Main Streamlit UI
├── agents.py                       # Core AI agent logic
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── mock_data/
│   ├── integrity_checklist.json   # Clause rules & scoring weights
│   └── mock_watchlist.json        # PEP vendors & price benchmarks
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| **Frontend** | Streamlit | Python-native UI, zero JS, instant deploy |
| **LLM** | Google Gemini 1.5 Flash | Free tier, strong BM/EN, fast |
| **PDF Parsing** | pypdf | Simple, reliable, no llama_index dependency |
| **Rules Engine** | JSON files | No live API deps, easy to extend |
| **Deployment** | Streamlit Community Cloud | Free, 1-click |

> **Note:** The original code used `llama_index.readers.file.PDFReader` which requires the optional `llama-index-readers-file` package. This version uses `pypdf` directly — simpler, faster, and more reliable for prototype use.

---

## ⚙️ Deploying to Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as the main file
4. Add `GEMINI_API_KEY` as a secret in the dashboard
5. Deploy!

---

## ⚠️ Known Limitations (v1 Prototype)

| Area | Current State | Future Upgrade |
|------|--------------|----------------|
| **Data** | Mock checklists & watchlists | Live SSM, MACC, ePerolehan APIs |
| **PDF** | Text-based PDFs only | OCR for scanned documents |
| **Auth** | None (open demo) | MyDigital ID / SSO |
| **Legal** | Advisory only | Legally binding compliance tool |
| **Security** | .env key management | PDPA-compliant pipeline, on-prem |

---

## 📚 References

- [Arahan Perbendaharaan 2023](https://www.treasury.gov.my)
- [MACC Act 2009](https://www.sprm.gov.my)
- [Open Contracting Data Standard](https://standard.open-contracting.org)
- [Malaysian Companies Act 2016 — Beneficial Ownership](https://www.ssm.com.my)

---

*⚠️ This is a prototype for demonstration purposes. Not legal advice. All AI outputs require human verification.*