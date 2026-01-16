import React from "react";

/**
 * Error Boundary Component
 * Catches errors in child components and displays error UI
 * Prevents entire app from crashing
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState((state) => ({
      error,
      errorInfo,
      errorCount: state.errorCount + 1,
    }));

    // Log to console in development
    console.error("Error caught by boundary:", error, errorInfo);

    // Could send to error tracking service (Sentry, etc)
    if (window.reportError) {
      window.reportError({
        error: error.toString(),
        errorInfo,
        timestamp: new Date().toISOString(),
      });
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={styles.container}>
          <div style={styles.card}>
            <h1 style={styles.title}>⚠️ Something went wrong</h1>

            <p style={styles.message}>
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>

            {process.env.NODE_ENV === "development" && (
              <details style={styles.details}>
                <summary style={styles.summary}>Error details</summary>
                <pre style={styles.errorText}>
                  {this.state.error && this.state.error.toString()}
                  {"\n\n"}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div style={styles.actions}>
              <button onClick={this.resetError} style={styles.buttonPrimary}>
                Try Again
              </button>
              <button
                onClick={() => (window.location.href = "/")}
                style={styles.buttonSecondary}
              >
                Go Home
              </button>
            </div>

            {this.state.errorCount > 3 && (
              <p style={styles.warning}>
                Multiple errors detected. Please <a href="/">refresh the page</a>.
              </p>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    backgroundColor: "#f5f5f5",
    padding: "20px",
  },
  card: {
    backgroundColor: "white",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
    padding: "40px",
    maxWidth: "500px",
    textAlign: "center",
  },
  title: {
    fontSize: "24px",
    color: "#d32f2f",
    marginBottom: "16px",
  },
  message: {
    fontSize: "16px",
    color: "#666",
    marginBottom: "24px",
  },
  details: {
    marginBottom: "24px",
    textAlign: "left",
  },
  summary: {
    cursor: "pointer",
    color: "#1976d2",
    marginBottom: "12px",
  },
  errorText: {
    backgroundColor: "#f0f0f0",
    padding: "12px",
    borderRadius: "4px",
    overflow: "auto",
    fontSize: "12px",
    maxHeight: "200px",
  },
  actions: {
    display: "flex",
    gap: "12px",
    justifyContent: "center",
  },
  buttonPrimary: {
    padding: "10px 20px",
    backgroundColor: "#1976d2",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
  },
  buttonSecondary: {
    padding: "10px 20px",
    backgroundColor: "transparent",
    color: "#1976d2",
    border: "1px solid #1976d2",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
  },
  warning: {
    marginTop: "20px",
    padding: "12px",
    backgroundColor: "#fff3cd",
    borderLeft: "4px solid #ffc107",
    color: "#856404",
    borderRadius: "4px",
  },
};

export default ErrorBoundary;
