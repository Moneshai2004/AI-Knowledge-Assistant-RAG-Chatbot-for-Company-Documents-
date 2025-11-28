"use client";

import Sidebar from "@/components/Sidebar";
import EvaluationUploadBox from "@/components/EvaluationUploadBox";
import EvaluationRunButton from "@/components/EvaluationRunButton";
import EvaluationList from "@/components/EvaluationList";

export default function EvaluationPage() {
  return (
    <div className="flex h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      <Sidebar />

      <main className="ml-0 flex-1 overflow-auto md:ml-64 px-6 py-6 space-y-6">
        <h1 className="text-xl font-semibold mb-2">Evaluation Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <EvaluationUploadBox />
          <EvaluationRunButton />
        </div>

        <EvaluationList />
      </main>
    </div>
  );
}
