export const createBaseUrl = (url: string) =>
  process.env.NODE_ENV === 'test' ? `http://localhost${url}` : url;
