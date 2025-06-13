export const createBaseUrl = (url: string) =>
  process.env.NODE_ENV === 'test' ? `https://localhost${url}` : url;
