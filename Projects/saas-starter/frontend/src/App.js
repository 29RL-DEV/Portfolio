import React, { useState } from "react";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [page, setPage] = useState("home");
  const [user, setUser] = useState(null);

  if (!user) {
    if (page === "login") return <Login onSuccess={() => setUser(true)} />;
    return <Home onLogin={() => setPage("login")} />;
  }

  return <Dashboard />;
}
