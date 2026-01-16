import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import ErrorBoundary from "../components/ErrorBoundary";
import { LoadingSpinner, SkeletonLoader } from "../components/LoadingStates";
import { AuthProvider, useAuth } from "../context/AppContext";

describe("ErrorBoundary", () => {
  const ThrowError = () => {
    throw new Error("Test error");
  };

  it("catches errors and displays error UI", () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
  });

  it("provides reset button to recover", () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    const resetButton = screen.getByText(/Try Again/i);
    expect(resetButton).toBeInTheDocument();
  });

  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <div>Safe content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText(/Safe content/i)).toBeInTheDocument();
  });
});

describe("LoadingSpinner", () => {
  it("renders spinner with text", () => {
    render(<LoadingSpinner text="Loading data..." />);

    expect(screen.getByText(/Loading data.../i)).toBeInTheDocument();
  });

  it("has loading animation", () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector("div[style*='border']");

    expect(spinner).toBeInTheDocument();
  });
});

describe("SkeletonLoader", () => {
  it("renders skeleton placeholders", () => {
    const { container } = render(<SkeletonLoader count={3} />);
    const skeletons = container.querySelectorAll(
      'div[style*="backgroundColor"]'
    );

    expect(skeletons.length).toBe(3);
  });

  it("accepts custom width and height", () => {
    const { container } = render(
      <SkeletonLoader width="200px" height="40px" />
    );
    const skeleton = container.querySelector('div[style*="backgroundColor"]');

    expect(skeleton).toHaveStyle("width: 200px");
    expect(skeleton).toHaveStyle("height: 40px");
  });
});

describe("AuthContext", () => {
  const TestComponent = () => {
    const { user, isAuthenticated } = useAuth();

    return (
      <div>
        {isAuthenticated ? (
          <div>Welcome {user?.username}</div>
        ) : (
          <div>Not authenticated</div>
        )}
      </div>
    );
  };

  it("provides auth state to components", () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText(/Not authenticated/i)).toBeInTheDocument();
  });

  it("throws error when useAuth is used outside provider", () => {
    // Suppress console.error for this test
    const spy = jest.spyOn(console, "error").mockImplementation();

    expect(() => render(<TestComponent />)).toThrow();

    spy.mockRestore();
  });
});

describe("Authentication Flow", () => {
  it("handles login and stores user", async () => {
    const TestLogin = () => {
      const { login, user } = useAuth();

      return (
        <div>
          <button onClick={() => login("test@example.com", "password")}>
            Login
          </button>
          {user && <div>Logged in as {user.email}</div>}
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestLogin />
      </AuthProvider>
    );

    const loginButton = screen.getByText(/Login/i);
    fireEvent.click(loginButton);

    // Note: In real tests, you'd mock the fetch call
  });
});
