import { defineConfig } from '@pandacss/dev';

export default defineConfig({
  preflight: true,

  // Include frontend app source and all frontend lib sources
  include: [
    './src/**/*.{js,jsx,ts,tsx}',
    '../../libs/frontend/*/src/**/*.{js,jsx,ts,tsx}',
  ],

  exclude: [],

  jsxFramework: 'react',

  theme: {
    extend: {
      tokens: {
        colors: {
          // Surface / background tiers
          surface: {
            DEFAULT: { value: '#0e0e0e' },
            containerLowest: { value: '#111111' },
            containerLow: { value: '#1a1a1a' },
            container: { value: '#222222' },
            containerHigh: { value: '#2a2a2a' },
            containerHighest: { value: '#333333' },
            bright: { value: '#3a3a3a' },
            variant: { value: '#444444' },
          },

          // Primary: Electric Lime
          primary: {
            DEFAULT: { value: '#f3ffca' },
            container: { value: '#cafd00' },
            dim: { value: '#a8d600' },
            onFixed: { value: '#1a1a00' },
          },

          // Secondary: Hot Pink
          secondary: {
            DEFAULT: { value: '#ff6b9b' },
            container: { value: '#ba005b' },
            onContainer: { value: '#ffd9e6' },
          },

          // Tertiary: Cyan
          tertiary: {
            DEFAULT: { value: '#a1faff' },
            container: { value: '#00f4fe' },
          },

          // Text
          onSurface: {
            DEFAULT: { value: '#ffffff' },
            variant: { value: '#9e9e9e' },
          },

          // Outline
          outline: {
            variant: { value: 'rgba(255, 255, 255, 0.15)' },
          },
        },

        fonts: {
          body: { value: "'Manrope', sans-serif" },
          heading: { value: "'Space Grotesk', sans-serif" },
        },

        fontSizes: {
          displayLg: { value: '3.5rem' },
          headlineLg: { value: '2rem' },
          bodyLg: { value: '1rem' },
          labelMd: { value: '0.75rem' },
        },

        letterSpacings: {
          tight: { value: '-0.02em' },
        },

        radii: {
          xl: { value: '0.75rem' },
          full: { value: '9999px' },
        },

        shadows: {
          ambient: { value: '0px 12px 24px rgba(0, 0, 0, 0.5)' },
          neonGlow: {
            value: '0px 12px 24px rgba(0, 0, 0, 0.5), 0px 0px 20px rgba(202, 253, 0, 0.1)',
          },
          neonPink: {
            value: '0px 0px 12px rgba(186, 0, 91, 0.4)',
          },
          neonCyan: {
            value: '0px 0px 4px rgba(0, 244, 254, 0.6)',
          },
        },

        blurs: {
          glass: { value: '20px' },
        },

        opacity: {
          glass: { value: '0.6' },
          ghostBorder: { value: '0.15' },
          ghostBorderActive: { value: '0.2' },
        },
      },

      keyframes: {
        pressDown: {
          '0%': { transform: 'scale(1)' },
          '100%': { transform: 'scale(0.98)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '20%': { transform: 'translateX(-8px)' },
          '40%': { transform: 'translateX(8px)' },
          '60%': { transform: 'translateX(-6px)' },
          '80%': { transform: 'translateX(6px)' },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
    },
  },

  // Panda output directory
  outdir: 'styled-system',

  // Allow libs to import from a stable package name instead of relative paths
  importMap: '@styled-system',
});
