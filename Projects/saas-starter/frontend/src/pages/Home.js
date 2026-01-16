import React from "react";

export default function Home({ onLogin }) {
  return (
    <div style={{ padding: 80, textAlign: "center" }}>
      <h1>AI Support for Your Website</h1>
      <p style={{ color: "#6b7280", maxWidth: 500, margin: "20px auto" }}>
        Turn visitors into customers with an AI assistant that answers
        instantly.
      </p>
      <button onClick={onLogin}>Start Free</button>
    </div>
  );
}
