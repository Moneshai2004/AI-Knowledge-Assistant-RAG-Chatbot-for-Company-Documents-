# Railway Production Deploy Instructions

1. Create Railway Project
2. Add **PostgreSQL** → copy DATABASE_URL.
3. Add **New Service → Deploy from GitHub (Dockerfile)**.
4. Add **Persistent Volume**:
   - mount path: `/app/data`
   - size: 5GB
5. Add Env Vars:

DATABASE_URL=<your real PG URL>
LORA_PATH=/app/lora_models/my_lora
DATA_DIR=/app/data
UPLOAD_DIR=/app/data/uploads
FAISS_DIR=/app/data/faiss
SECRET_KEY=your_secret


6. Deploy.