/**
 * Design System - Centralized styling constants
 * Ensures consistency across entire application
 */

// Color Palette
export const colors = {
  // Primary
  primary: "#1976d2",
  primaryLight: "#42a5f5",
  primaryDark: "#1565c0",

  // Secondary
  secondary: "#dc004e",
  secondaryLight: "#f73378",
  secondaryDark: "#c2185b",

  // Status Colors
  success: "#4caf50",
  successLight: "#81c784",
  successDark: "#388e3c",

  warning: "#ff9800",
  warningLight: "#ffb74d",
  warningDark: "#f57c00",

  error: "#d32f2f",
  errorLight: "#ef5350",
  errorDark: "#c62828",

  info: "#2196f3",
  infoLight: "#64b5f6",
  infoDark: "#1976d2",

  // Neutral
  white: "#ffffff",
  black: "#000000",
  gray50: "#fafafa",
  gray100: "#f5f5f5",
  gray200: "#eeeeee",
  gray300: "#e0e0e0",
  gray400: "#bdbdbd",
  gray500: "#9e9e9e",
  gray600: "#757575",
  gray700: "#616161",
  gray800: "#424242",
  gray900: "#212121",

  // Transparent
  transparent: "transparent",
};

// Typography
export const typography = {
  // Font families
  fontFamily: {
    primary:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
    mono: "'Courier New', 'Courier', monospace",
  },

  // Font sizes
  fontSize: {
    xs: "12px",
    sm: "14px",
    base: "16px",
    lg: "18px",
    xl: "20px",
    "2xl": "24px",
    "3xl": "30px",
    "4xl": "36px",
  },

  // Font weights
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // Line heights
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2,
  },
};

// Spacing
export const spacing = {
  xs: "4px",
  sm: "8px",
  md: "16px",
  lg: "24px",
  xl: "32px",
  "2xl": "48px",
  "3xl": "64px",
};

// Border Radius
export const borderRadius = {
  none: "0px",
  sm: "4px",
  md: "8px",
  lg: "12px",
  xl: "16px",
  full: "9999px",
};

// Shadows
export const shadows = {
  none: "none",
  sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
  base: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
  md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
  lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
  xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
};

// Breakpoints for responsive design
export const breakpoints = {
  xs: "320px",
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
};

// Z-index scale
export const zIndex = {
  hide: -1,
  auto: "auto",
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  backdrop: 1300,
  modal: 1400,
  popover: 1500,
  tooltip: 1600,
};

// Transition/Animation
export const transitions = {
  duration: {
    shortest: "150ms",
    shorter: "200ms",
    short: "250ms",
    standard: "300ms",
    complex: "375ms",
    enteringScreen: "225ms",
    leavingScreen: "195ms",
  },
  timing: {
    easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    easeOut: "cubic-bezier(0.0, 0, 0.2, 1)",
    easeIn: "cubic-bezier(0.4, 0, 1, 1)",
    linear: "linear",
  },
};

// Common component styles
export const componentStyles = {
  button: {
    primary: {
      backgroundColor: colors.primary,
      color: colors.white,
      border: "none",
      padding: `${spacing.sm} ${spacing.md}`,
      borderRadius: borderRadius.md,
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.medium,
      cursor: "pointer",
      transition: `all ${transitions.duration.short} ${transitions.timing.easeInOut}`,
      "&:hover": {
        backgroundColor: colors.primaryDark,
      },
      "&:active": {
        transform: "scale(0.98)",
      },
      "&:disabled": {
        opacity: 0.6,
        cursor: "not-allowed",
      },
    },
    secondary: {
      backgroundColor: colors.gray100,
      color: colors.gray900,
      border: `1px solid ${colors.gray300}`,
      padding: `${spacing.sm} ${spacing.md}`,
      borderRadius: borderRadius.md,
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.medium,
      cursor: "pointer",
      transition: `all ${transitions.duration.short} ${transitions.timing.easeInOut}`,
    },
  },
  card: {
    backgroundColor: colors.white,
    border: `1px solid ${colors.gray200}`,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    boxShadow: shadows.md,
  },
  input: {
    padding: `${spacing.sm} ${spacing.md}`,
    border: `1px solid ${colors.gray300}`,
    borderRadius: borderRadius.md,
    fontSize: typography.fontSize.base,
    fontFamily: typography.fontFamily.primary,
    "&:focus": {
      outline: "none",
      borderColor: colors.primary,
      boxShadow: `0 0 0 3px ${colors.primary}20`,
    },
  },
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  breakpoints,
  zIndex,
  transitions,
  componentStyles,
};
