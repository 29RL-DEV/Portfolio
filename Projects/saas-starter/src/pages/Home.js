import React from "react";

export default function Home({ onLogin }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
      }}
    >
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
          cursor: "pointer",
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

      <div style={{ padding: 80, textAlign: "center" }}>
        <h1>AI Support for Your Website</h1>
        <p style={{ color: "#6b7280", maxWidth: 500, margin: "20px auto" }}>
          Turn visitors into customers with an AI assistant that answers
          instantly.
        </p>
        <button onClick={onLogin}>Start Free</button>
      </div>
    </div>
  );
}
