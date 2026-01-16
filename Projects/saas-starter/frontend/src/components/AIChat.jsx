import { useState } from "react";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function AIChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages(m => [...m, userMsg]);
    setInput("");
    setLoading(true);

    const res = await fetch(`${API}/api/ai/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await res.json();
    setMessages(m => [...m, { role: "assistant", content: data.reply }]);
    setLoading(false);
  }

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 16 }}>
      <h3>AI Assistant</h3>
      <div style={{ height: 300, overflowY: "auto", marginBottom: 10 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 6, textAlign: m.role === "user" ? "right" : "left" }}>
            <b>{m.role === "user" ? "You" : "AI"}:</b> {m.content}
          </div>
        ))}
        {loading && <div>AI is typing...</div>}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask the AI…" />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
