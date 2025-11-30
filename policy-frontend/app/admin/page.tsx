"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import SystemStats from "@/components/SystemStats";
import QueryLogTable from "@/components/QueryLogTable";
import AdminCard from "@/components/AdminCard";

import { mergeIndexes, getAdminStats, getQueryLogs } from "@/lib/api";

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [mergeRes, setMergeRes] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(true);

  // --------------------------
  // Fetch stats
  // --------------------------
  const fetchStats = async () => {
    const data = await getAdminStats();
    setStats(data);
    setLoadingStats(false);
  };

  // --------------------------
  // Fetch logs
  // --------------------------
  const fetchLogs = async () => {
    const data = await getQueryLogs();
    setLogs(data);
    setLoadingLogs(false);
  };

  useEffect(() => {
    fetchStats();
    fetchLogs();
  }, []);

  // --------------------------
  // Handle merge
  // --------------------------
  const handleMerge = async () => {
    const r = await mergeIndexes();
    setMergeRes(r);
    fetchStats(); // refresh stats
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50">
      <Sidebar />

      <main className="ml-0 flex-1 px-6 pt-8 md:ml-64">
        <h1 className="text-xl font-semibold">Admin Dashboard</h1>
        <p className="mb-6 text-sm text-slate-400">
          System monitoring, logs, and index management.
        </p>

        {/* ---- System Stats ---- */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-3">System Stats</h2>
          <SystemStats stats={stats} loading={loadingStats} />
        </section>

        {/* ---- Index Controls ---- */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold mb-3">Index Management</h2>

          <AdminCard>
            <button
              onClick={handleMerge}
              className="rounded bg-blue-600 px-4 py-2 text-sm hover:bg-blue-500"
            >
              Merge All Indexes
            </button>
          </AdminCard>

          {mergeRes && (
            <pre className="mt-4 rounded border border-slate-800 bg-slate-900 p-4 text-xs">
              {JSON.stringify(mergeRes, null, 2)}
            </pre>
          )}
        </section>

        {/* ---- Query Logs ---- */}
        <section>
          <h2 className="text-lg font-semibold mb-3">Recent Query Logs</h2>
          <QueryLogTable logs={logs} loading={loadingLogs} />
        </section>
      </main>
    </div>
  );
}
