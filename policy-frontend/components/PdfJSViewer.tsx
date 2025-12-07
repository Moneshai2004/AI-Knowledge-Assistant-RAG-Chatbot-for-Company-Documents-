"use client";

import { useEffect, useRef, useState } from "react";

// ✅ Modern PDF.js build compatible with Webpack + Vercel
import * as pdfjsLib from "pdfjs-dist/webpack.mjs";
import workerSrc from "pdfjs-dist/build/pdf.worker.mjs?url";

// Set worker
pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc;

interface Props {
  fileUrl: string;
  targetPage?: number;
}

export default function PdfJSViewer({ fileUrl, targetPage }: Props) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const [pdf, setPdf] = useState<any>(null);

  // Load PDF in browser
  useEffect(() => {
    if (!fileUrl) return;
    const task = pdfjsLib.getDocument(fileUrl);
    task.promise.then(setPdf);
  }, [fileUrl]);

  // Render pages
  useEffect(() => {
    if (!pdf) return;

    const container = viewerRef.current;
    if (!container) return;

    const renderPages = async () => {
      container.innerHTML = "";

      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: 1.2 });

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d")!;
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        const wrapper = document.createElement("div");
        wrapper.style.marginBottom = "16px";
        wrapper.appendChild(canvas);
        container.appendChild(wrapper);

        await page.render({ canvasContext: ctx, viewport }).promise;

        if (targetPage === pageNum) {
          setTimeout(() => {
            wrapper.scrollIntoView({ behavior: "smooth" });
          }, 300);
        }
      }
    };

    renderPages();
  }, [pdf, targetPage]);

  return (
    <div
      ref={viewerRef}
      className="overflow-y-scroll h-full p-2 rounded-xl bg-muted/30"
    />
  );
}
