import React from "react";

/**
 * Skeleton Loader Component
 * Shows placeholder while content is loading
 */
export function SkeletonLoader({ width = "100%", height = "20px", count = 1 }) {
  const skeletons = Array.from({ length: count }, (_, i) => (
    <div
      key={i}
      style={{
        width,
        height,
        backgroundColor: "#e0e0e0",
        borderRadius: "4px",
        marginBottom: "12px",
        animation: "pulse 1.5s ease-in-out infinite",
      }}
    />
  ));

  return (
    <>
      <style>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
      {skeletons}
    </>
  );
}

/**
 * Card Skeleton
 */
export function CardSkeleton() {
  return (
    <div style={{ padding: "16px", backgroundColor: "white", borderRadius: "8px" }}>
      <SkeletonLoader width="60%" height="24px" />
      <SkeletonLoader count={3} height="16px" />
    </div>
  );
}

/**
 * Loading Spinner
 */
export function LoadingSpinner({ size = "40px", text = "Loading..." }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px",
      }}
    >
      <div
        style={{
          width: size,
          height: size,
          border: "4px solid #f0f0f0",
          borderTop: "4px solid #1976d2",
          borderRadius: "50%",
          animation: "spin 1s linear infinite",
        }}
      />
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      {text && <p style={{ marginTop: "12px", color: "#666" }}>{text}</p>}
    </div>
  );
}

/**
 * Wrapper component for loading states
 */
export function LoadingWrapper({ isLoading, error, children, fallback = null }) {
  if (isLoading) {
    return fallback || <LoadingSpinner />;
  }

  if (error) {
    return (
      <div
        style={{
          padding: "20px",
          backgroundColor: "#ffebee",
          color: "#c62828",
          borderRadius: "4px",
          border: "1px solid #ef5350",
        }}
      >
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return children;
}
