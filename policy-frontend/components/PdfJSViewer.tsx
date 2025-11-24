"use client";

import { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf";

pdfjsLib.GlobalWorkerOptions.workerSrc = "/pdf.worker.js";

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
    if (!pdf || !viewerRef.current) return;

    const container = viewerRef.current;

    (async () => {
      container.innerHTML = "";

      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: 1.2 });

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const wrapper = document.createElement("div");
        wrapper.style.marginBottom = "20px";
        wrapper.appendChild(canvas);

        container.appendChild(wrapper);

        await page.render({
          canvasContext: ctx!,
          viewport,
        }).promise;

        if (targetPage && targetPage === pageNum) {
          setTimeout(() => {
            wrapper.scrollIntoView({ behavior: "smooth" });
          }, 200);
        }
      }
    })();
  }, [pdf, targetPage]);

  return (
    <div ref={viewerRef} className="overflow-y-scroll h-full p-2 bg-muted/30" />
  );
}
