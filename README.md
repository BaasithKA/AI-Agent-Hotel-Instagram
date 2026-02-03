# AI Agent – Hotel Social Media Automation System

AI Agent berbasis Python & FastAPI untuk otomatisasi konten Instagram hotel:
scraping data, AI caption generation, dan auto-publishing ke Instagram.

## 🚀 Fitur Utama

- Automated hotel scraping (Firecrawl)
- AI content generation (Google Gemini)
- Background bot scheduler (APScheduler)
- Auto-posting via Make.com webhook
- Monitoring dashboard (Next.js)

## 🧠 Tech Stack

**Backend**

- Python 3.10+, FastAPI
- PostgreSQL, SQLModel
- APScheduler
- Google Gemini (LLM)
- Firecrawl

**Frontend**

- Next.js 14 (App Router)
- Tailwind CSS

## ⚙️ Cara Menjalankan

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
