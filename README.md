# AI Knowledge Assistant (RAG Chatbot for Company Documents)

## 🚀 Overview
An AI chatbot that allows company employees to query internal documents (PDFs) using natural language. Powered by LangChain, FAISS, and Groq API.

## ⚙️ Tech Stack
- **Frontend:** Streamlit (MVP)
- **Backend:** FastAPI
- **AI Layer:** LangChain + SentenceTransformers
- **Vector Store:** FAISS
- **Deployment:** Render + Streamlit Cloud

## ▶️ Local Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
streamlit run frontend/streamlit_app.py

