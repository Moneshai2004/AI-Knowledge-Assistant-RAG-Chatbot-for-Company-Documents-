"use client";

import { useMemo, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import DocumentList, { DocumentMeta } from "@/components/DocumentList";
import PdfJSViewer from "@/components/PdfJSViewer"; // ✅ FIXED IMPORT

const POLICY_DOCUMENTS: DocumentMeta[] = [
  {
    id: "employee-handbook",
    title: "Employee Handbook",
    fileName: "Employee_Handbook.pdf",
  },
  {
    id: "leave-policy",
    title: "Leave & Attendance Policy",
    fileName: "Leave_Policy.pdf",
  },
  {
    id: "it-security",
    title: "IT & Security Policy",
    fileName: "IT_Security_Policy.pdf",
  },
];

export default function DocumentsPage() {
  const [selectedId, setSelectedId] = useState<string | undefined>(
    POLICY_DOCUMENTS[0]?.id
  );

  const search = useSearchParams();
  const file = search.get("file");
  const pageQuery = search.get("page");

  // Auto-select the correct PDF from citation
  useEffect(() => {
    if (file) {
      const found = POLICY_DOCUMENTS.find((d) => d.fileName === file);
      if (found) setSelectedId(found.id);
    }
  }, [file]);

  const selectedDoc = useMemo(() => {
    return POLICY_DOCUMENTS.find((d) => d.id === selectedId);
  }, [selectedId]);

  return (
    <main className="h-[calc(100vh-2rem)] w-full px-4 py-4 md:px-8">
      <div className="h-full flex flex-col gap-3">
        <section className="flex-1 grid grid-cols-1 md:grid-cols-[0.35fr_0.65fr] gap-3 h-full">
          {/* LEFT: LIST */}
          <DocumentList
            documents={POLICY_DOCUMENTS}
            selectedId={selectedId}
            onSelect={(doc) => setSelectedId(doc.id)}
          />

          {/* RIGHT: PDF VIEWER */}
          <PdfJSViewer
            fileUrl={selectedDoc ? `/policies/${selectedDoc.fileName}` : ""}
            targetPage={pageQuery ? parseInt(pageQuery) : undefined}
          />
        </section>
      </div>
    </main>
  );
}
