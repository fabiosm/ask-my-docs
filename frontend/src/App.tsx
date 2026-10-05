import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [answer, setAnswer] = useState("");
  const [uploaded, setUploaded] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");
    setUploading(true);

    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      if (!res.ok) {
        throw new Error(`Upload failed (${res.status})`);
      }
      const data = await res.json();
      console.log("Upload response:", data);

      setUploaded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  function handleAsk(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const question = new FormData(e.currentTarget).get("question") as string;
    if (!question.trim()) return;
    setError("");
    setAnswer("");
    setAsking(true);

    const source = new EventSource(`${API}/ask?question=${encodeURIComponent(question)}`);

    let received = false;
    source.onmessage = (event) => {
      received = true;
      setAsking(false);
      setAnswer((prev) => prev + event.data);
    };

    source.onerror = () => {
      source.close();
      setAsking(false);
      if (!received) setError("Failed to get an answer. Is the backend running?");
    };
  }

  return (
    <div style={{ maxWidth: 640, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Ask My Docs</h1>

      <input type="file" accept=".pdf" onChange={handleUpload} disabled={uploading} />
      {uploading && <p>⏳ Processing PDF...</p>}
      {uploaded && !uploading && <p>✅ PDF processed</p>}

      <form onSubmit={handleAsk} style={{ marginTop: 16 }}>
        <input name="question" placeholder="Ask a question..." style={{ width: "70%" }} />
        <button type="submit" disabled={asking || uploading}>
          {asking ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && <p style={{ color: "crimson" }}>⚠️ {error}</p>}

      <div style={{ marginTop: 16, whiteSpace: "pre-wrap", background: "#f4f4f4", padding: 16, minHeight: 60 }}>
        {asking && !answer && <em>Waiting for the model...</em>}
        {answer}
      </div>
    </div>
  )
}

export default App