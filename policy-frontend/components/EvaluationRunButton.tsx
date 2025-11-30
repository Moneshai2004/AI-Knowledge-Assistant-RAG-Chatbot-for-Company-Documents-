"use client";

import { useState } from "react";
import { runEvaluation } from "@/lib/evaluation";

export default function EvaluationRunButton() {
  const [status, setStatus] = useState<string | null>(null);

  const onRun = async () => {
    setStatus("Starting evaluation…");
    const res = await runEvaluation();
    setStatus(res.message);
  };

  return (
    <div className="rounded-xl border p-6 bg-white dark:bg-slate-900 shadow-sm">
      <h2 className="text-lg font-semibold mb-2">Run Evaluation</h2>
      <p className="text-xs text-slate-500 mb-4">
        Starts evaluating all Q&A against the RAG system.
      </p>

      <button
        onClick={onRun}
        className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white"
      >
        Run Evaluation
      </button>

      {status && (
        <p className="text-xs mt-3 text-emerald-400 animate-pulse">{status}</p>
      )}
    </div>
  );
}
