import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      // See empty-module.ts — keeps pdfjs-dist's Node-only `canvas` require
      // out of the browser bundle.
      canvas: "./empty-module.ts",
    },
  },
};

export default nextConfig;
