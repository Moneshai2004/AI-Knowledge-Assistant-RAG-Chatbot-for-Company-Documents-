"use client";

import { useEffect, useState } from "react";
import { listEvaluations } from "@/lib/evaluation";

export default function EvaluationList() {
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    listEvaluations().then(setRows);
  }, []);

  return (
    <div className="rounded-xl border p-6 bg-white dark:bg-slate-900 shadow-sm">
      <h2 className="text-lg font-semibold mb-3">Evaluation Runs</h2>

      {rows.length === 0 ? (
        <p className="text-xs text-slate-400">No evaluation runs found.</p>
      ) : (
        <ul className="space-y-3">
          {rows.map((ev) => (
            <li
              key={ev.id}
              className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800 border"
            >
              <p className="text-sm font-medium">Run #{ev.id}</p>
              <p className="text-xs text-slate-500">
                Score:{" "}
                <span className="font-semibold text-indigo-500">
                  {ev.score ?? "?"}
                </span>
              </p>
              <p className="text-[10px] text-slate-500">
                {new Date(ev.run_at).toLocaleString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
