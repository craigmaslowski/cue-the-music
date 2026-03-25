/**
 * Design token constants from "Digital Neon Tactility" design system.
 * These mirror the Panda CSS config tokens for use in JS logic
 * (e.g., conditional styling, canvas drawing) where css() is not available.
 */

export const colorTokens = {
  primary: {
    container: '#cafd00',
    DEFAULT: '#f3ffca',
    dim: '#a8d600',
    onFixed: '#1a1a00',
  },
  secondary: {
    container: '#ba005b',
    DEFAULT: '#ff6b9b',
    onContainer: '#ffd9e6',
  },
  surface: {
    bright: '#3a3a3a',
    container: '#222222',
    containerHigh: '#2a2a2a',
    containerHighest: '#333333',
    containerLow: '#1a1a1a',
    containerLowest: '#111111',
    DEFAULT: '#0e0e0e',
    variant: '#444444',
  },
  tertiary: {
    container: '#00f4fe',
    DEFAULT: '#a1faff',
  },
} as const;

export const fontTokens = {
  body: "'Manrope', sans-serif",
  heading: "'Space Grotesk', sans-serif",
} as const;
