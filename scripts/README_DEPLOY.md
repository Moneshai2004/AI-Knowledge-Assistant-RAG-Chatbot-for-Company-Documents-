# 🚀 Deployment Guide

## 1. Backend (Railway)
- Create project
- Add PostgreSQL
- Add Volume (`/app/data`)
- Deploy backend using Dockerfile
- Set environment variables:
  - DATABASE_URL=postgresql+asyncpg://...
  - DATA_DIR=/app/data
  - UPLOAD_DIR=/app/data/uploads
  - FAISS_DIR=/app/data/faiss
  - LORA_PATH=/app/lora_models/my_lora

## 2. Frontend (Vercel)
- Connect GitHub repo
- Set env vars:
  - NEXT_PUBLIC_API_BASE="https://<railway-backend-url>"
- Deploy

## 3. Verify

### Backend:
curl https://<railway-backend-url>/
curl https://<railway-backend-url>/documents/list


### Frontend:
- Upload PDF
- Ask question
- Check LoRA responses



---

# 🚀 **3. RAILWAY DEPLOYMENT STEPS**

1. Go to Railway dashboard  
2. Create new project  
3. Add **PostgreSQL**  
4. Add new service → **Deploy from GitHub (backend folder)**  
5. Add **Volume**  
   - Mount path: `/app/data`  
6. Add env vars:



DATABASE_URL=postgresql+asyncpg://...
DATA_DIR=/app/data
UPLOAD_DIR=/app/data/uploads
FAISS_DIR=/app/data/faiss
LORA_PATH=/app/lora_models/my_lora
SECRET_KEY=xxxxx


7. Deploy  
8. Visit URL: `https://yourbackend.up.railway.app`

---

# 🚀 **4. VERCEL DEPLOYMENT STEPS**

1. Go to https://vercel.com  
2. Import your GitHub repo  
3. Set environment variable:



NEXT_PUBLIC_API_BASE=https://your-backend-url.up.railway.app


4. Deploy  
5. Open app

---

# 🎯 **5. FINAL VERIFICATION**

### Backend test:


curl https://your-backend.up.railway.app/


### LoRA test:


curl -X POST https://your-backend/ask
 -d '{"question":"hello"}'


### FAISS test:
Index a document, ensure registry updates.

---

# ✅ Deployment package is complete  
If you want next:

- CI/CD workflow  
- NGINX reverse proxy (optional)  
- Custom domain setup  
- Auto scale tuning  
- Security tightening  
