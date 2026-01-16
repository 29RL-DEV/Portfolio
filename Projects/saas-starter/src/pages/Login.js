import React, { useState } from "react";
import { login } from "../api";

export default function Login({ onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function submit() {
    const data = await login(email, password);
    if (data.token) onSuccess();
    else alert("Login failed");
  }

  return (
    <div style={{ 
      minHeight: "100vh",
      display: "flex", 
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      position: "relative"
    }}>
      {/* Back to Portfolio */}
      <a
        href="/"
        style={{
          position: "fixed",
          top: "20px",
          left: "20px",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          gap: "8px",
          background: "rgba(0, 0, 0, 0.7)",
          backdropFilter: "blur(8px)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          color: "#10b981",
          padding: "10px 16px",
          borderRadius: "8px",
          fontSize: "0.95rem",
          fontWeight: 600,
          textDecoration: "none",
          boxShadow: "0 8px 16px rgba(0, 0, 0, 0.5)",
          transition: "all 0.2s",
          pointerEvents: "auto",
          cursor: "pointer"
        }}
        onMouseEnter={(e) => {
          e.target.style.background = "rgba(0, 0, 0, 0.9)";
          e.target.style.transform = "translateX(-2px)";
          e.target.style.boxShadow = "0 12px 24px rgba(0, 0, 0, 0.6)";
        }}
        onMouseLeave={(e) => {
          e.target.style.background = "rgba(0, 0, 0, 0.7)";
          e.target.style.transform = "translateX(0)";
          e.target.style.boxShadow = "0 8px 16px rgba(0, 0, 0, 0.5)";
        }}
      >
        <i className="fas fa-arrow-left"></i>
        Portfolio
      </a>

      <div style={{ maxWidth: 400, margin: "100px auto" }}>
      <h2>Login</h2>
      <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <input
        type="password"
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={submit}>Login</button>
    </div>
  );
}
