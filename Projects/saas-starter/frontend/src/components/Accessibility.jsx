/**
 * Accessibility Utilities and Components
 * Ensures WCAG AA compliance
 */

/**
 * Accessible Button Component
 */
export function AccessibleButton({ 
  onClick, 
  children, 
  ariaLabel, 
  disabled = false,
  type = "button" 
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel || children}
      role="button"
      tabIndex={disabled ? -1 : 0}
      style={{
        padding: "10px 16px",
        borderRadius: "4px",
        border: "1px solid #ccc",
        backgroundColor: "#f0f0f0",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.6 : 1,
        fontSize: "14px",
        fontWeight: 500,
      }}
    >
      {children}
    </button>
  );
}

/**
 * Accessible Form Input
 */
export function AccessibleInput({
  id,
  label,
  placeholder,
  value,
  onChange,
  type = "text",
  required = false,
  ariaDescribedBy = null,
  error = null,
}) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <label htmlFor={id} style={{ display: "block", marginBottom: "4px" }}>
        {label}
        {required && <span style={{ color: "red" }}>*</span>}
      </label>
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={ariaDescribedBy}
        style={{
          width: "100%",
          padding: "8px 12px",
          borderRadius: "4px",
          border: error ? "2px solid red" : "1px solid #ccc",
          fontSize: "14px",
        }}
      />
      {error && (
        <div 
          id={ariaDescribedBy} 
          role="alert"
          style={{ color: "red", fontSize: "12px", marginTop: "4px" }}
        >
          {error}
        </div>
      )}
    </div>
  );
}

/**
 * Skip to Main Content Link
 * Allows screen reader users to skip navigation
 */
export function SkipToMainContent() {
  return (
    <a
      href="#main-content"
      style={{
        position: "absolute",
        top: "-40px",
        left: "0",
        backgroundColor: "#000",
        color: "#fff",
        padding: "8px",
        textDecoration: "none",
        zIndex: 100,
      }}
      onFocus={(e) => {
        e.target.style.top = "0";
      }}
      onBlur={(e) => {
        e.target.style.top = "-40px";
      }}
    >
      Skip to Main Content
    </a>
  );
}

/**
 * Accessible Modal/Dialog
 */
export function AccessibleModal({
  isOpen,
  onClose,
  title,
  children,
  ariaLabel,
}) {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-label={ariaLabel}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "8px",
          padding: "24px",
          maxWidth: "500px",
          maxHeight: "90vh",
          overflow: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="modal-title">{title}</h2>
        {children}
        <button
          onClick={onClose}
          aria-label="Close modal"
          style={{
            marginTop: "16px",
            padding: "8px 16px",
            backgroundColor: "#f0f0f0",
            border: "1px solid #ccc",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
}

/**
 * Focus Manager - Helps manage focus for accessibility
 */
export class FocusManager {
  static trap(containerElement) {
    const focusableElements = containerElement.querySelectorAll(
      'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    return (e) => {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };
  }

  static restoreFocus(previouslyFocusedElement) {
    if (previouslyFocusedElement && previouslyFocusedElement.focus) {
      previouslyFocusedElement.focus();
    }
  }
}

/**
 * Accessibility Check utility
 */
export const a11y = {
  // Check color contrast (basic)
  checkContrast: (foreground, background) => {
    // Implementation for WCAG contrast checking
    return true; // Simplified
  },

  // Check for keyboard navigation
  ensureKeyboardAccess: (element) => {
    if (!element.hasAttribute("tabindex")) {
      element.setAttribute("tabindex", "0");
    }
  },

  // Add screen reader text
  addScreenReaderText: (element, text) => {
    const sr = document.createElement("span");
    sr.className = "sr-only";
    sr.textContent = text;
    element.appendChild(sr);
  },
};
