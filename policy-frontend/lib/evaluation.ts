import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export const evalApi = axios.create({
  baseURL: API_BASE,
});

// Upload JSON
export const uploadEvalDataset = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await evalApi.post("/evaluation/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

// Run evaluation job
export const runEvaluation = async () => {
  const res = await evalApi.post("/evaluation/run");
  return res.data;
};

// List runs
export const listEvaluations = async () => {
  const res = await evalApi.get("/evaluation/list");
  return res.data;
};
