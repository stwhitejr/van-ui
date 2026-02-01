export const formatFileSize = (bytes?: number): string => {
  return (() => {
    if (!bytes) {
      return '';
    }
    return (() => {
      if (bytes < 1024) {
        return `${bytes} B`;
      }
      return (() => {
        if (bytes < 1024 * 1024) {
          return `${(bytes / 1024).toFixed(1)} KB`;
        }
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
      })();
    })();
  })();
};

export const isImageFile = (filename: string): boolean => {
  const imageExtensions = [
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.bmp',
    '.webp',
    '.svg',
    '.ico',
  ];
  const lowerFilename = filename.toLowerCase();
  return imageExtensions.some((ext) => lowerFilename.endsWith(ext));
};

