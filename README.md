# 🧠 AI Form Generator

This repository contains the backend and core architecture for the **AI-Form-Generator**, a FastAPI-based system that uses Anthropic’s Claude models to automatically generate and schedule structured data-collection forms for research or clinical studies.

---

## 🚀 Current Status
✅ FastAPI backend running  
✅ Claude API key connected  
✅ Virtual environment configured (`.venv`)  
✅ Local server live at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧩 Folder Structure

ai-form-generator/
├── backend/
│ ├── main.py
│ ├── requirements.txt
│ └── .env
├── implementation_roadmap.md
├── technical_specification.md
├── quick_start_guide.md
└── PROJECT_SUMMARY.md

---

## ⚙️ Tech Stack
- **Python 3.11+**
- **FastAPI**
- **Anthropic Claude API**
- **Uvicorn** (development server)
- **dotenv** (for secure environment variable management)

---

## 🧠 Project Summary
This project automates the creation and scheduling of research data-capture forms using AI.  
It aims to make study setup faster, reduce human error, and let non-technical users build reliable digital forms with guided AI support.

---

## 🔧 Run Locally
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload

Then visit http://127.0.0.1:8000
🌱 Next Steps

Integrate form schema validation

Implement scheduling logic (LCM)

Build front-end UI for form creation

Add logging and security layers
👤 Author

Ihtesham Ul-Haq (Sham Baig)
MSc Artificial Intelligence with Business Strategy, Aston University (2025–2026)
