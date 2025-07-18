import axios from "axios";

/**
 * Where is the back‑end?
 * – in dev (`npm run dev`) VITE_API_BASE is usually empty → proxy works
 * – in prod we set it to https://rag-api.athenalabo.com
 */
const API = import.meta.env.VITE_API_BASE ?? "";

export const uploadPdf = (file: File) => {
  const form = new FormData();
  form.append("file", file);

  return axios.post(`${API}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const askQuestion = (question: string) =>
  axios.post(`${API}/ask`, new URLSearchParams({ question }));
