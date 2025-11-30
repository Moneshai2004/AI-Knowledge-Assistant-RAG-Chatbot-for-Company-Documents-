import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";


export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});
// ✅ Add JWT automatically to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ----------------------
// /ask
// ----------------------
export const askQuestion = async (question: string) => {
  try {
    const res = await api.post("/ask/", { question });
    return res.data;
  } catch (err: any) {
    console.error("askQuestion error:", err);
    throw err;
  }
};

// ----------------------
// /upload
// ----------------------
export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await api.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  } catch (err) {
    console.error("uploadPDF error:", err);
    throw err;
  }
};

// ----------------------
// /admin/merge
// ----------------------
export const mergeIndexes = async () => {
  try {
    const res = await api.post("/admin/merge");
    return res.data;
  } catch (err) {
    console.error("mergeIndexes error:", err);
    throw err;
  }
};

// ----------------------
// /admin/stats
// ----------------------
export const getAdminStats = async () => {
  try {
    const res = await api.get("/admin/stats");
    return res.data;
  } catch (err) {
    console.error("getAdminStats error:", err);
    return null;
  }
};

// ----------------------
// /admin/query-logs
// ----------------------
export const getQueryLogs = async (limit = 50) => {
  try {
    const res = await api.get(`/admin/query-logs?limit=${limit}`);
    return res.data;
  } catch (err) {
    console.error("getQueryLogs error:", err);
    return [];
  }
};
