export function openDocument(fileName: string, page?: number) {
  const url = `/documents?file=${encodeURIComponent(fileName)}${
    page ? `&page=${page}` : ""
  }`;

  window.open(url, "_blank");
}
