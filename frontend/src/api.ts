import axios from 'axios';

export const uploadPdf = (file: File) => {
  const form = new FormData();
  form.append('file', file);
  return axios.post('/upload', form);
};

export const askQuestion = (question: string) =>
  axios.post('/ask', new URLSearchParams({ question }));
