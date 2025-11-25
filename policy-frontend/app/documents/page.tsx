"use client";

import { useMemo, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import DocumentList, { DocumentMeta } from "@/components/DocumentList";
import PdfJSViewer from "@/components/PdfJSViewer";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [selectedId, setSelectedId] = useState<string | undefined>();

  const search = useSearchParams();
  const file = search.get("file");
  const pageQuery = search.get("page");

  // Load documents dynamically from backend
  useEffect(() => {
    const api = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

    fetch(`${api}/documents/list`)
      .then((res) => res.json())
      .then((data) => {
        const mapped = data.map((d: any) => ({
          id: d.id,
          title: d.id.replace(/_/g, " "),
          fileName: d.file_name,
        }));

        setDocuments(mapped);

        // Default select first document
        if (!selectedId && mapped.length > 0) {
          setSelectedId(mapped[0].id);
        }
      });
  }, []);

  // When citation triggers "?file=<fname>"
  useEffect(() => {
    if (file && documents.length > 0) {
      const found = documents.find((d) => d.fileName === file);
      if (found) setSelectedId(found.id);
    }
  }, [file, documents]);

  const selectedDoc = useMemo(() => {
    return documents.find((d) => d.id === selectedId);
  }, [documents, selectedId]);

  return (
    <main className="h-[calc(100vh-2rem)] w-full px-4 py-4 md:px-8">
      <div className="h-full flex flex-col gap-3">
        <section className="flex-1 grid grid-cols-1 md:grid-cols-[0.35fr_0.65fr] gap-3 h-full">
          {/* LEFT LIST */}
          <DocumentList
            documents={documents}
            selectedId={selectedId}
            onSelect={(doc) => setSelectedId(doc.id)}
          />

          {/* RIGHT VIEWER */}
          <PdfJSViewer
            fileUrl={selectedDoc ? `/policies/${selectedDoc.fileName}` : ""}
            targetPage={pageQuery ? parseInt(pageQuery) : undefined}
          />
        </section>
      </div>
    </main>
  );
}
