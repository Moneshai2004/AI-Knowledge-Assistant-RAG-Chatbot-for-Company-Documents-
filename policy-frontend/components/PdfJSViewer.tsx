"use client";

import { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist/webpack.mjs";

// 👇 Correct worker import for Next.js 16 / Turbopack
import workerURL from "pdfjs-dist/build/pdf.worker.mjs";

pdfjsLib.GlobalWorkerOptions.workerSrc = workerURL;

interface Props {
  fileUrl: string;
  targetPage?: number;
}

export default function PdfJSViewer({ fileUrl, targetPage }: Props) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const [pdf, setPdf] = useState<any>(null);

  useEffect(() => {
    if (!fileUrl) return;
    const task = pdfjsLib.getDocument(fileUrl);
    task.promise.then(setPdf);
  }, [fileUrl]);

  useEffect(() => {
    if (!pdf) return;

    const container = viewerRef.current;
    if (!container) return;

    const render = async () => {
      container.innerHTML = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
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

        if (targetPage === i) {
          wrapper.scrollIntoView({ behavior: "smooth" });
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
