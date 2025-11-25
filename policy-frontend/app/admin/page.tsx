"use client";
import AdminTools from "@/components/AdminTools";

import Sidebar from "@/components/Sidebar";
import { mergeIndexes } from "@/lib/api";
import { useState } from "react";

export default function AdminPage() {
  const [res, setRes] = useState<any>(null);

  const handleMerge = async () => {
    const r = await mergeIndexes();
    setRes(r);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50">
      <Sidebar />
      <main className="ml-0 flex-1 px-6 pt-8 md:ml-64">
        <h1 className="text-xl font-semibold">Admin Tools</h1>
        <p className="mb-6 text-sm text-slate-400">
          Manage FAISS indexes and retrieval resources.
        </p>

        <AdminTools />

        {res && (
          <pre className="mt-6 rounded border border-slate-800 bg-slate-900 p-4 text-xs">
            {JSON.stringify(res, null, 2)}
          </pre>
        )}
      </main>
    </div>
  );
}
