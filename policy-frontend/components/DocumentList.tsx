"use client";

export interface DocumentMeta {
  id: string; // backend doc_id
  title: string; // human-friendly title
  fileName: string; // actual PDF file name
  description?: string;
  category?: string;
}

interface DocumentListProps {
  documents: DocumentMeta[];
  selectedId?: string;
  onSelect: (doc: DocumentMeta) => void;
}

export default function DocumentList({
  documents,
  selectedId,
  onSelect,
}: DocumentListProps) {
  if (!documents.length) {
    return (
      <div className="h-full flex items-center justify-center text-xs text-muted-foreground border rounded-2xl">
        No documents found. Upload a PDF first.
      </div>
    );
  }

  return (
    <div className="h-full rounded-2xl border bg-background overflow-hidden flex flex-col">
      {/* HEADER */}
      <div className="px-4 py-2 border-b">
        <p className="text-sm font-semibold">Policy Documents</p>
        <p className="text-xs text-muted-foreground">
          Select a file to preview and navigate citations
        </p>
      </div>

      {/* LIST */}
      <div className="flex-1 overflow-y-auto">
        <ul className="divide-y text-sm">
          {documents.map((doc) => {
            const isActive = doc.id === selectedId;

            return (
              <li key={doc.id}>
                <button
                  type="button"
                  onClick={() => onSelect(doc)}
                  className={[
                    "w-full text-left px-4 py-3 flex flex-col gap-1",
                    "transition",
                    isActive
                      ? "bg-indigo-100 dark:bg-indigo-900/40 border-l-4 border-l-indigo-600"
                      : "hover:bg-muted/60",
                  ].join(" ")}
                >
                  {/* TITLE */}
                  <span className="font-medium truncate">{doc.title}</span>

                  {/* FILE NAME */}
                  <span className="text-[10px] text-muted-foreground truncate">
                    {doc.fileName}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
