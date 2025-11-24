"use client";

interface SourceBubbleProps {
  chunkId: number;
  page?: number;
  text: string;
  fileName: string;
  onOpen: () => void;
}

export default function SourceBubble({
  chunkId,
  page,
  text,
  fileName,
  onOpen,
}: SourceBubbleProps) {
  return (
    <button
      onClick={onOpen}
      className="group w-full text-left rounded-lg border 
      bg-slate-100 dark:bg-slate-900 px-3 py-2 mb-2 shadow-sm 
      hover:bg-slate-200 dark:hover:bg-slate-800 transition"
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium">Source • Page {page ?? "?"}</span>
        <span className="text-[10px] text-slate-500">{fileName}</span>
      </div>

      <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-3">
        {text}
      </p>
    </button>
  );
}
