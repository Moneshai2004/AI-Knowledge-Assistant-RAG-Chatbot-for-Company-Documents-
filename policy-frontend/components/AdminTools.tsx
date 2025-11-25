"use client";

import { useState } from "react";
import { mergeIndexes } from "@/lib/api";

export default function AdminTools() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleMerge = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await mergeIndexes();
      setResult(res);
    } catch (err: any) {
      console.error(err);
      setError("Failed to merge indexes. Check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-4 mt-6">
      {/* MERGE INDEXES */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="text-sm font-semibold mb-2">Merge FAISS Indexes</h2>
        <p className="text-xs text-slate-400 mb-4">
          Combine all existing FAISS index files into one global index used by
          the chatbot.
        </p>

        <button
          onClick={handleMerge}
          disabled={loading}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white
          disabled:bg-slate-600"
        >
          {loading ? "Merging…" : "Run Merge"}
        </button>
      </div>

      {/* RESULT */}
      {result && (
        <pre className="rounded-lg bg-slate-900 p-4 text-xs border border-slate-700 overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

      {/* ERROR */}
      {error && (
        <div className="rounded-lg bg-red-900/30 text-red-300 px-3 py-2 text-xs">
          {error}
        </div>
      )}
    </div>
  );
}
