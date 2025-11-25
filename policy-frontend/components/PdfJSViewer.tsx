"use client";

import { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf";
import "pdfjs-dist/web/pdf_viewer.css";

// 🟢 CRITICAL FIX: Point worker to CDN
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

interface Props {
  fileUrl: string;
  targetPage?: number;
}

export default function PdfJSViewer({ fileUrl, targetPage }: Props) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const [pdf, setPdf] = useState<any>(null);

  // Load PDF
  useEffect(() => {
    if (!fileUrl) return;

    const task = pdfjsLib.getDocument(fileUrl);
    task.promise.then(setPdf);
  }, [fileUrl]);

  // Render PDF
  useEffect(() => {
    if (!pdf) return;
    const container = viewerRef.current;
    if (!container) return;

    const render = async () => {
      container.innerHTML = "";

      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: 1.2 });

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const wrapper = document.createElement("div");
        wrapper.style.marginBottom = "16px";
        wrapper.appendChild(canvas);
        container.appendChild(wrapper);

        await page.render({ canvasContext: ctx!, viewport }).promise;

        if (targetPage && pageNum === targetPage) {
          setTimeout(() => {
            wrapper.scrollIntoView({ behavior: "smooth", block: "start" });
          }, 300);
        }
      }
    };

    render();
  }, [pdf, targetPage]);

  return (
    <div
      ref={viewerRef}
      className="overflow-y-scroll h-full p-2 rounded-xl bg-muted/30"
    />
  );
}
