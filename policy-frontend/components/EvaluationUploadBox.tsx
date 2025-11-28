"use client";

import { useState } from "react";
import { uploadEvalDataset } from "@/lib/evaluation";

export default function EvaluationUploadBox() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onFileSelected = (f: File | null) => {
    if (!f) return;
    if (!f.name.endsWith(".json")) {
      setError("Upload a valid JSON file.");
      return;
    }
    setError(null);
    setFile(f);
  };

  const onUpload = async () => {
    if (!file) return;

    setStatus("Uploading...");
    setError(null);

    try {
      const res = await uploadEvalDataset(file);
      setStatus(`Uploaded successfully • ${res.items} items`);
    } catch (err) {
      setError("Failed to upload dataset");
    }
  };

  return (
    <div className="rounded-xl border p-6 bg-white dark:bg-slate-900 shadow-sm">
      <h2 className="text-lg font-semibold mb-2">Upload Dataset</h2>
      <p className="text-xs text-slate-500 mb-4">
        Upload evaluation dataset (JSON with list of Q&A).
      </p>

      <input
        type="file"
        accept=".json"
        onChange={(e) => onFileSelected(e.target.files?.[0] || null)}
        className="text-sm"
      />

      <button
        onClick={onUpload}
        className="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
      >
        Upload
      </button>

      {status && (
        <p className="text-xs mt-2 text-emerald-500 font-medium">{status}</p>
      )}
      {error && <p className="text-xs mt-2 text-red-500">{error}</p>}
    </div>
  );
}
