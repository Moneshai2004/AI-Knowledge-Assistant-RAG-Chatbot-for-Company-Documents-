"use client";

import { useState, DragEvent, ChangeEvent } from "react";
import { uploadPDF } from "@/lib/api";

export default function PDFUploadBox() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (f: File | null) => {
    if (!f) return;
    if (f.type !== "application/pdf") {
      setError("Please select a PDF file.");
      setFile(null);
      return;
    }
    setError(null);
    setStatus(null);
    setFile(f);
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files?.[0];
    handleFileSelect(dropped || null);
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const picked = e.target.files?.[0] || null;
    handleFileSelect(picked);
  };

  const onUpload = async () => {
    if (!file || isUploading) return;

    setIsUploading(true);
    setStatus("Uploading and indexing PDF…");
    setError(null);

    try {
      const res = await uploadPDF(file);
      // You can customize based on backend response shape
      setStatus(
        `Uploaded & indexing started. doc_id=${res.doc_id || "?"}, chunks=${
          res.chunks_indexed || "?"
        }`
      );
    } catch (err: any) {
      console.error(err);
      setError("Upload failed. Check backend logs.");
      setStatus(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        className="border-2 border-dashed rounded-2xl px-6 py-10 flex flex-col items-center justify-center 
        bg-slate-50 dark:bg-slate-900/40 border-slate-300 dark:border-slate-700
        text-center cursor-pointer"
      >
        <p className="text-sm font-medium mb-2">Drag & drop a PDF here</p>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
          or click to choose a file from your computer
        </p>

        <input
          type="file"
          accept="application/pdf"
          className="hidden"
          id="pdf-input"
          onChange={onFileChange}
        />
        <label
          htmlFor="pdf-input"
          className="inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-xs font-medium text-white
          hover:bg-indigo-700 transition"
        >
          Choose PDF
        </label>

        {file && (
          <div className="mt-4 text-xs text-slate-700 dark:text-slate-200">
            <p className="font-medium truncate max-w-xs">
              Selected: {file.name}
            </p>
            <p className="text-[11px] text-slate-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={onUpload}
          disabled={!file || isUploading}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white
          disabled:bg-slate-400 disabled:cursor-not-allowed"
        >
          {isUploading ? "Uploading…" : "Upload & Index"}
        </button>

        {file && !isUploading && (
          <button
            onClick={() => {
              setFile(null);
              setStatus(null);
              setError(null);
            }}
            className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
          >
            Clear selection
          </button>
        )}
      </div>

      {status && (
        <div className="text-xs rounded-lg bg-emerald-50 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200 px-3 py-2">
          {status}
        </div>
      )}

      {error && (
        <div className="text-xs rounded-lg bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-200 px-3 py-2">
          {error}
        </div>
      )}
    </div>
  );
}
