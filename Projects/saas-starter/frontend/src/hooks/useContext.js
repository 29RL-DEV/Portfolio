import { useContext } from "react";
import { AuthContext, BillingContext, UIContext } from "./AppContext";

/**
 * Custom hook to use Auth Context
 * Ensures context is used within provider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

/**
 * Custom hook to use Billing Context
 */
export function useBilling() {
  const context = useContext(BillingContext);
  if (!context) {
    throw new Error("useBilling must be used within BillingProvider");
  }
  return context;
}

/**
 * Custom hook to use UI Context
 */
export function useUI() {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error("useUI must be used within UIProvider");
  }
  return context;
}

/**
 * Combined hook for common use case: auth + notifications
 */
export function useAuthWithNotifications() {
  const auth = useAuth();
  const ui = useUI();

  return {
    ...auth,
    notify: ui.addNotification,
  };
}
