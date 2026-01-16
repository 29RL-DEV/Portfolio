// LoginForm Component - User authentication and registration
// Handles JWT token-based login and new user registration
// Features: Dual-tab interface, input validation, error handling, loading states

import React, { useState } from "react";
import axios from "axios";

const API =
  process.env.REACT_APP_API_URL || "https://todo-manager-api-ux4e.onrender.com";
/**
 * LoginForm - Authentication component
 *
 * Features:
 * - Login tab: Authenticate existing users
 * - Register tab: Create new user accounts
 * - JWT token handling: Stores access/refresh tokens in localStorage
 * - Input validation: Client-side validation before submission
 * - Error handling: Displays server-side errors to user
 *
 * API Endpoints:
 * - POST /api/token/ - Get JWT tokens (username + password)
 * - POST /api/auth/register/ - Create new user account
 */
const LoginForm = ({ onLoginSuccess }) => {
  // Login form state
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  // Registration form state
  const [registerData, setRegisterData] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("login"); // 'login' or 'register'

  // Handle login form input changes
  const handleLoginChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle register form input changes
  const handleRegisterChange = (e) => {
    setRegisterData({ ...registerData, [e.target.name]: e.target.value });
  };

  /**
   * Submit login form
   * Sends credentials to backend to get JWT tokens
   * Stores tokens and triggers parent component update
   */
  const handleLogin = async (e) => {
    e.preventDefault();

    // Validate inputs
    if (!formData.username.trim() || !formData.password.trim()) {
      setError("Please enter both username and password");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Request JWT tokens from backend
      const res = await axios.post(`${API}/api/token/`, formData);

      // Store tokens in localStorage for future requests
      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);

      // Notify parent component that login was successful
      onLoginSuccess();
    } catch (err) {
      // Handle different error types
      if (err.response?.status === 401) {
        setError("Invalid username or password");
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Login failed. Please try again.");
      }
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Submit registration form
   * Creates new user account on backend
   * Automatically switches to login tab on success
   */
  const handleRegister = async (e) => {
    e.preventDefault();

    // Client-side validation
    if (
      !registerData.username.trim() ||
      !registerData.email.trim() ||
      !registerData.password.trim()
    ) {
      setError("Please fill in all fields");
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(registerData.email)) {
      setError("Please enter a valid email address");
      return;
    }

    // Validate password length
    if (registerData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    // Validate password confirmation
    if (registerData.password !== registerData.password2) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Send registration request to backend
      await axios.post(`${API}/api/auth/register/`, registerData);

      // Clear form and switch to login tab
      setRegisterData({ username: "", email: "", password: "", password2: "" });
      setActiveTab("login");
      alert("Registration successful! Please log in with your credentials.");
    } catch (err) {
      // Handle different error responses
      if (err.response?.data?.username?.[0]) {
        setError(err.response.data.username[0]);
      } else if (err.response?.data?.email?.[0]) {
        setError(err.response.data.email[0]);
      } else if (err.response?.data?.password?.[0]) {
        setError(err.response.data.password[0]);
      } else {
        setError("Registration failed. Please try again.");
      }
      console.error("Registration error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 flex items-center justify-center p-4">
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

      <div className="bg-blue-950 bg-opacity-80 backdrop-blur-md rounded-2xl shadow-2xl p-8 w-full max-w-md border border-blue-700">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-block mb-4">
            <i className="fas fa-tasks text-4xl text-blue-300"></i>
          </div>
          <h1 className="text-3xl font-bold text-blue-100 mb-2">
            Todo-Manager
          </h1>
          <p className="text-blue-300">
            Organize and manage your tasks efficiently
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 bg-blue-900 bg-opacity-50 p-1 rounded-lg">
          <button
            onClick={() => {
              setActiveTab("login");
              setError("");
            }}
            className={`flex-1 py-2 px-4 rounded-md font-semibold transition ${
              activeTab === "login"
                ? "bg-blue-600 text-white shadow-lg"
                : "bg-transparent text-blue-300 hover:text-blue-100"
            }`}
          >
            <i className="fas fa-sign-in-alt mr-2"></i>Login
          </button>
          <button
            onClick={() => {
              setActiveTab("register");
              setError("");
            }}
            className={`flex-1 py-2 px-4 rounded-md font-semibold transition ${
              activeTab === "register"
                ? "bg-blue-600 text-white shadow-lg"
                : "bg-transparent text-blue-300 hover:text-blue-100"
            }`}
          >
            <i className="fas fa-user-plus mr-2"></i>Register
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-6 flex items-start gap-2">
            <i className="fas fa-exclamation-circle flex-shrink-0 mt-0.5"></i>
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        {activeTab === "login" ? (
          <form onSubmit={handleLogin}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  <i className="fas fa-user mr-2"></i>Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleLoginChange}
                  placeholder="Enter your username"
                  className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
                  required
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  <i className="fas fa-lock mr-2"></i>Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleLoginChange}
                  placeholder="Enter your password"
                  className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
                  required
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <i className="fas fa-spinner animate-spin"></i>
                    Logging in...
                  </>
                ) : (
                  <>
                    <i className="fas fa-sign-in-alt"></i>
                    Login
                  </>
                )}
              </button>
            </div>
          </form>
        ) : (
          // Register Form
          <form onSubmit={handleRegister}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  <i className="fas fa-user mr-2"></i>Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={registerData.username}
                  onChange={handleRegisterChange}
                  placeholder="Choose a username"
                  className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
                  required
                  disabled={loading}
                  minLength="3"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  <i className="fas fa-envelope mr-2"></i>Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={registerData.email}
                  onChange={handleRegisterChange}
                  placeholder="Enter your email"
                  className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
                  required
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  <i className="fas fa-lock mr-2"></i>Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={registerData.password}
                  onChange={handleRegisterChange}
                  placeholder="Create a password (min 6 chars)"
                  className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
                  required
                  disabled={loading}
                  minLength="6"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  <i className="fas fa-check-circle mr-2"></i>Confirm Password
                </label>
                <input
                  type="password"
                  name="password2"
                  value={registerData.password2}
                  onChange={handleRegisterChange}
                  placeholder="Confirm your password"
                  className="w-full px-4 py-2 bg-blue-900 border border-blue-600 rounded-lg text-white placeholder-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
                  required
                  disabled={loading}
                  minLength="6"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <i className="fas fa-spinner animate-spin"></i>
                    Registering...
                  </>
                ) : (
                  <>
                    <i className="fas fa-user-plus"></i>
                    Register
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        {/* Footer */}
        <p className="text-center text-blue-300 text-sm mt-6">
          All your tasks are securely stored and synchronized across devices
        </p>
      </div>

      {/* Back to Portfolio Button - 2cm spacing (75px) */}
      <div style={{ marginTop: "75px" }} className="flex justify-center">
        <a
          href="https://29rl.dev/?from=portfolio&return=/"
          className="bg-black/60 backdrop-blur-md border border-white/10 text-green-400 px-6 py-2 rounded-lg text-sm font-semibold shadow-lg hover:bg-black/80 transition inline-flex items-center gap-2 whitespace-nowrap"
        >
          ← Back to Portfolio
        </a>
      </div>
    </div>
  );
};

export default LoginForm;
