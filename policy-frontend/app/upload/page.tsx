"use client";

import Sidebar from "@/components/Sidebar";
import PDFUploadBox from "@/components/PDFUploadBox";

export default function UploadPage() {
  return (
    <div
      className="flex h-screen 
      bg-white text-slate-900 
      dark:bg-slate-950 dark:text-slate-50"
    >
      <Sidebar />

      <main className="ml-0 flex-1 overflow-hidden md:ml-64">
        <div className="flex h-full flex-col px-4 py-4 md:px-8 md:py-6">
          <header className="mb-4">
            <h1 className="text-lg font-semibold tracking-tight">
              Upload & Index Policy PDFs
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xl">
              Upload new policy documents. They&apos;ll be chunked, embedded,
              and added to the search index used by the AI assistant.
            </p>
          </header>

          <PDFUploadBox />
        </div>
      </main>
    </div>
  );
}
