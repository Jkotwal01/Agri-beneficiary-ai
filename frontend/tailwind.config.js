/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        background: '#F8FAFC', // Slate 50
        surface: '#FFFFFF',
        primary: '#0F172A', // Slate 900
        secondary: '#475569', // Slate 600
        accent: {
          emerald: '#059669', // Golden records
          sky: '#0284C7', // Action workflows
          amber: '#D97706', // Low confidence
        },
        borderline: '#E2E8F0', // Slate 200
      },
      borderRadius: {
        'sm': '4px',
        DEFAULT: '6px',
        'md': '6px',
      },
      fontSize: {
        'xs': '11px',
        'sm': '12px',
        'base': '13px',
      }
    },
  },
  plugins: [],
}
