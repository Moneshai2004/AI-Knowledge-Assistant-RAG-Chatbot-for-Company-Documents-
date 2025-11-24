"use client";

export interface DocumentMeta {
  id: string;
  title: string;
  fileName: string; // e.g. "Employee_Handbook.pdf"
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
        No documents configured.
      </div>
    );
  }

  return (
    <div className="h-full rounded-2xl border bg-background overflow-hidden flex flex-col">
      <div className="px-4 py-2 border-b">
        <p className="text-sm font-medium">Policy Documents</p>
        <p className="text-xs text-muted-foreground">
          Select a file to preview and chat about it.
        </p>
      </div>

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
                    "w-full text-left px-4 py-3 flex flex-col gap-0.5",
                    "transition",
                    isActive
                      ? "bg-primary/10 border-l-4 border-l-primary"
                      : "hover:bg-muted/60",
                  ].join(" ")}
                >
                  <span className="font-medium truncate">{doc.title}</span>
                  {doc.description && (
                    <span className="text-xs text-muted-foreground truncate">
                      {doc.description}
                    </span>
                  )}
                  <span className="text-[10px] text-muted-foreground">
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
