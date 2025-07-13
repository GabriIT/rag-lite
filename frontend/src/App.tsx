import { useState } from "react";
import { uploadPdf, askQuestion } from "./api";

export default function App() {
  const [pdf, setPdf] = useState<File>();
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const upload = async () => {
    if (!pdf) return;
    setBusy(true);
    await uploadPdf(pdf);
    setBusy(false);
    alert("PDF indexed 🎉");
  };

  const ask = async () => {
    if (!question.trim()) return;
    setBusy(true);
    const { data } = await askQuestion(question);
    setChat((c) => [...c, `🧑: ${question}`, `🤖: ${data.response}`]);
    setQuestion("");
    setBusy(false);
  };

  return (
    <main className="p-6 max-w-xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Lite-RAG Demo</h1>

      {/* Upload box */}
      <section className="border p-4 rounded space-y-2 bg-white">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setPdf(e.target.files?.[0])}
        />
        <button
          onClick={upload}
          disabled={busy || !pdf}
          className="bg-blue-600 disabled:bg-blue-300 text-white px-3 py-1 rounded"
        >
          {busy ? "Uploading…" : "Upload & Index"}
        </button>
      </section>

      {/* Ask box */}
      <section className="border p-4 rounded space-y-2 bg-white">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the PDF…"
          className="border w-full p-2 rounded"
        />
        <button
          onClick={ask}
          disabled={busy || !question}
          className="bg-green-600 disabled:bg-green-300 text-white px-3 py-1 rounded"
        >
          {busy ? "Processing…" : "Ask"}
        </button>
      </section>

      {/* Chat log */}
      <section className="border p-4 rounded max-h-96 overflow-auto bg-white space-y-1">
        {chat.map((line, i) => (
          <p key={i} className={line.startsWith("🤖") ? "font-semibold" : ""}>
            {line}
          </p>
        ))}
      </section>
    </main>
  );
}
