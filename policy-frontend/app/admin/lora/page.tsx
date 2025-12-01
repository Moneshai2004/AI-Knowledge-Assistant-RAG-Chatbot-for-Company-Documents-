"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

export default function LoraPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState<any>(null);
  const [message, setMessage] = useState("");

  // -----------------------------
  // Fetch LoRA status
  // -----------------------------
  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/admin/lora/status`);
      setStatus(res.data);
    } catch (err) {
      console.error("Status error:", err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  // -----------------------------
  // Upload LoRA File
  // -----------------------------
  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await axios.post(`${API_BASE}/admin/lora/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(`Uploaded: ${res.data.path}`);
      fetchStatus();
    } catch (err) {
      console.error(err);
      setMessage("Upload failed");
    }
  };

  // -----------------------------
  // Load LoRA adapter
  // -----------------------------
  const handleLoad = async () => {
    if (!selectedFile) {
      setMessage("Upload a LoRA file first.");
      return;
    }

    const path = `lora_adapters/${selectedFile.name}`;

    try {
      await axios.post(`${API_BASE}/admin/lora/load`, null, {
        params: { path },
      });

      setMessage("LoRA loaded successfully!");
      fetchStatus();
    } catch (err) {
      console.error(err);
      setMessage("Failed to load LoRA");
    }
  };

  // -----------------------------
  // Unload LoRA
  // -----------------------------
  const handleUnload = async () => {
    try {
      await axios.post(`${API_BASE}/admin/lora/unload`);
      setMessage("LoRA unloaded.");
      fetchStatus();
    } catch (err) {
      console.error(err);
      setMessage("Failed to unload LoRA");
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50">
      <Sidebar />

      <main className="flex-1 p-8 md:ml-64">
        <h1 className="text-xl font-semibold mb-4">LoRA Management</h1>

        {message && <div className="mb-4 text-sm text-blue-400">{message}</div>}

        {/* Status */}
        <div className="bg-slate-900 border border-slate-800 p-4 rounded mb-6">
          <h2 className="text-lg font-semibold mb-2">Current Status</h2>
          {status && (
            <pre className="text-sm">{JSON.stringify(status, null, 2)}</pre>
          )}
        </div>

        {/* Upload */}
        <div className="bg-slate-900 border border-slate-800 p-4 rounded mb-6">
          <h2 className="text-lg font-semibold mb-2">Upload LoRA File</h2>

          <input
            type="file"
            className="text-sm mb-3"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />

          <button
            onClick={handleUpload}
            className="rounded bg-blue-600 px-4 py-2 text-sm hover:bg-blue-500 mr-3"
          >
            Upload
          </button>

          <button
            onClick={handleLoad}
            className="rounded bg-green-600 px-4 py-2 text-sm hover:bg-green-500"
          >
            Load LoRA
          </button>
        </div>

        {/* Unload */}
        <div className="bg-slate-900 border border-slate-800 p-4 rounded">
          <button
            onClick={handleUnload}
            className="rounded bg-red-600 px-4 py-2 text-sm hover:bg-red-500"
          >
            Unload LoRA
          </button>
        </div>
      </main>
    </div>
  );
}
