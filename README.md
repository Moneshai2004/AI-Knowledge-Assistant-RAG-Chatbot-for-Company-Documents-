# AI HR Policy Assistant

An internal AI-powered assistant that answers company HR and policy questions
using a **Retrieval-Augmented Generation (RAG)** pipeline with **hybrid FAISS + BM25 retrieval**
and **LoRA-controlled generation**, ensuring accurate, citation-backed answers
with zero hallucination tolerance.

<!-- Optional Social Preview Image -->
<!--
![AI HR Policy Assistant](https://socialify.git.ci/<YOUR_GITHUB_USERNAME>/<REPO_NAME>/image?description=1&font=Inter&language=1&name=1&theme=Dark)
-->

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-orange)
![RAG](https://img.shields.io/badge/RAG-Hybrid%20Search-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 🚀 Project Demo

📌 **Live Demo:** _Not publicly deployed_

This project is designed as an **internal enterprise AI system**.
Deployment details are intentionally omitted.

However, the repository includes:
- End-to-end backend and frontend code
- Admin dashboard
- Evaluation pipeline
- PDF ingestion and retrieval flow

## 📸 Project Screenshots

Medium post[https://medium.com/@moneshshanmugam/building-a-production-grade-ai-hr-policy-assistant-rag-lora-fastapi-next-js-0e8cf6fc8853]

- Chat interface with citations
- PDF viewer with page navigation
- Admin dashboard (stats & logs)
- Evaluation dashboard

<!--
![Chat UI](screenshots/chat.png)
![Admin Dashboard](screenshots/admin.png)
-->

## ✨ Features

- 📄 PDF upload & semantic chunking
- 🔍 Hybrid retrieval (FAISS + BM25)
- ⚖️ Score fusion with tunable alpha
- 📎 Citation-based answers with page references
- 🧠 LoRA fine-tuned generation (style-only)
- 🧪 Retrieval evaluation pipeline
- 📊 Admin dashboard (stats, logs, index merge)
- 🔐 JWT-protected admin APIs
- ⚙️ Async background indexing


## ⚙️ Installation Steps

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>

cd backend
python -m venv venv
source venv/bin/activate   # Linux / Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt


uvicorn app.main:app --reload

3️⃣ Start backend
uvicorn app.main:app --reload

4️⃣ Frontend setup
cd frontend
npm install
npm run dev


📌 Backend runs on http://localhost:8000
📌 Frontend runs on http://localhost:3000


---

# ✅ Step 7: Contribution Guidelines (Optional)

```md
## 🤝 Contribution Guidelines

This is currently a personal learning and portfolio project.

Suggestions, bug reports, and improvements are welcome via issues.
Please discuss major changes before opening a pull request.

✅ Step 8: Technologies Used (Optional)
## 🛠️ Technologies Used

### Backend
- FastAPI
- SQLModel + SQLite
- FAISS
- Sentence Transformers
- Transformers + PEFT (LoRA)
- PyMuPDF

### Frontend
- Next.js (App Router)
- Tailwind CSS
- PDF.js

✅ Step 9: License Information (Optional)
## 📄 License

This project is licensed under the MIT License.


(Only include this if you actually add an MIT LICENSE file.)

✅ Step 10: Support Information (Optional)
## 💬 Support

If you have questions about:
- RAG system design
- Hybrid retrieval
- FAISS indexing
- Evaluation strategies

Feel free to open an issue or reach out via LinkedIn.
