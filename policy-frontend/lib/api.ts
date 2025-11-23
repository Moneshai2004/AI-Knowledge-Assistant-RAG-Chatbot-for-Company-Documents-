import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// POST /ask/
export const askQuestion = async (question: string) => {
  const res = await api.post("/ask/", { question });
  return res.data;
};

// POST /upload/
export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};

// POST /admin/merge
export const mergeIndexes = async () => {
  const res = await api.post("/admin/merge");
  return res.data;
};
