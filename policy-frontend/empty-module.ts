// Stub for the optional Node-only `canvas` package.
//
// pdfjs-dist reaches for `require("canvas")` in three places (DOMMatrix and
// CanvasRenderingContext2D polyfills, and NodeCanvasFactory). Every one of them
// sits behind an `isNodeJS` guard, so none of it runs in the browser — but the
// bundler resolves the require statically and fails the build regardless.
//
// `canvas` is a native Node addon and is deliberately not a dependency of this
// project: PdfJSViewer is a "use client" component that renders through the
// browser's own <canvas>. Aliasing the import here keeps it out of the bundle.
export default {};
