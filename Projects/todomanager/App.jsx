import React, { useState, useEffect } from "react";
import "./src/styles.css";
import TaskList from "./src/components/TaskList";
import LoginForm from "./src/components/LoginForm";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-blue-900 text-white">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Oops! Something went wrong</h2>
            <p className="text-gray-300 mb-6">{this.state.error?.message}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-green-600 px-6 py-2 rounded hover:bg-green-700 transition"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function checkAuth() {
      try {
        const token = localStorage.getItem("access");

        if (!token) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        const response = await fetch(
          `${import.meta.env.VITE_API_URL || "https://todo-manager-api-ux4e.onrender.com"}/api/auth/me/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          },
        );

        if (response.ok) {
          setIsAuthenticated(true);
        } else if (response.status === 401) {
          localStorage.clear();
          setIsAuthenticated(false);
        } else {
          throw new Error(`Auth check failed: ${response.status}`);
        }
      } catch (err) {
        console.error("Auth check error:", err);
        setError("Failed to check authentication");
        localStorage.clear();
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    }

    checkAuth();
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setIsAuthenticated(false);
    setError(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-blue-900 text-white text-xl">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-blue-900 text-white">
        <nav className="bg-blue-950 p-4 flex justify-between items-center gap-4 shadow-lg">
          <h1 className="text-2xl font-bold text-green-400 flex-1 text-center">
            📋 Task Manager
          </h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 px-4 py-2 rounded hover:bg-red-700 transition font-semibold whitespace-nowrap"
          >
            Logout
          </button>
        </nav>

        {error && (
          <div className="bg-red-600/20 border border-red-500 text-red-200 p-4 m-4 rounded">
            {error}
          </div>
        )}

        <main className="p-4">
          <ErrorBoundary>
            <TaskList />
          </ErrorBoundary>
        </main>

        <footer className="text-center text-gray-400 text-sm p-4 mt-8">
          Task Manager v1.0 • Built with Django + React
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
