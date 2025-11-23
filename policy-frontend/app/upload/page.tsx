"use client";

import Sidebar from "@/components/Sidebar";
import { uploadPDF } from "@/lib/api";
import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleUpload = async () => {
    if (!file) return;
    const res = await uploadPDF(file);
    setResult(res);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50">
      <Sidebar />
      <main className="ml-0 flex-1 px-6 pt-8 md:ml-64">
        <h1 className="text-xl font-semibold">Upload PDF</h1>
        <p className="mb-6 text-sm text-slate-400">
          Upload policy or HR documents for indexing.
        </p>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-sm"
        />

        <button
          onClick={handleUpload}
          className="mt-4 rounded bg-indigo-600 px-4 py-2 text-sm"
        >
          Upload
        </button>

        {result && (
          <pre className="mt-6 rounded border border-slate-800 bg-slate-900 p-4 text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </main>
    </div>
  );
}
