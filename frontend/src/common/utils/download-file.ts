export const downloadFileByLink = (link: string, filename: string): void => {
  const element = document.createElement('a');
  element.setAttribute('href', link);
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
  setTimeout(() => URL.revokeObjectURL(link), 0);
};

export const downloadFileByBlob = (blob: Blob, filename: string): void => {
  if (!blob || !filename) return;
  const link = URL.createObjectURL(blob);
  downloadFileByLink(link, filename);
};
