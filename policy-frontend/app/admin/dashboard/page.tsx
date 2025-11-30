"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { api } from "@/lib/api";

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const resStats = await api.get("/admin/stats");
      const resLogs = await api.get("/admin/query-logs");

      setStats(resStats.data);
      setLogs(resLogs.data);
    } catch (err) {
      console.error("Dashboard load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading)
    return (
      <div className="flex h-screen items-center justify-center text-white">
        Loading...
      </div>
    );

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50">
      <Sidebar />

      <main className="ml-0 flex-1 px-6 pt-8 md:ml-64">
        <h1 className="text-xl font-semibold mb-6">Admin Dashboard</h1>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          <div className="bg-slate-900 p-4 rounded border border-slate-800">
            <h2 className="text-sm text-slate-400">Total Documents</h2>
            <p className="text-xl font-semibold">{stats.total_documents}</p>
          </div>

          <div className="bg-slate-900 p-4 rounded border border-slate-800">
            <h2 className="text-sm text-slate-400">Total Chunks</h2>
            <p className="text-xl font-semibold">{stats.total_chunks}</p>
          </div>

          <div className="bg-slate-900 p-4 rounded border border-slate-800">
            <h2 className="text-sm text-slate-400">Total Queries</h2>
            <p className="text-xl font-semibold">{stats.total_queries}</p>
          </div>
        </div>

        {/* Logs */}
        <h2 className="text-lg font-semibold mb-3">Recent Queries</h2>

        <div className="bg-slate-900 rounded border border-slate-800 p-4 max-h-[400px] overflow-y-auto">
          {logs.map((item: any) => (
            <div key={item.id} className="border-b border-slate-800 py-2">
              <p className="text-sm">{item.query_text}</p>
              <p className="text-xs text-slate-500">{item.timestamp}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
