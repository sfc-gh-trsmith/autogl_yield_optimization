/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        snowcore: {
          50: '#e6f4ff',
          100: '#b3dcff',
          200: '#80c4ff',
          300: '#4dacff',
          400: '#1a94ff',
          500: '#0077e6',
          600: '#005cb3',
          700: '#004180',
          800: '#00264d',
          900: '#000b1a',
        },
        terafield: {
          50: '#fff4e6',
          100: '#ffdcb3',
          200: '#ffc480',
          300: '#ffac4d',
          400: '#ff941a',
          500: '#e67700',
          600: '#b35c00',
          700: '#804100',
          800: '#4d2600',
          900: '#1a0c00',
        },
        autogl: {
          50: '#f0e6ff',
          100: '#d1b3ff',
          200: '#b380ff',
          300: '#944dff',
          400: '#761aff',
          500: '#5c00e6',
          600: '#4700b3',
          700: '#320080',
          800: '#1d004d',
          900: '#08001a',
        },
        risk: {
          low: '#10b981',
          medium: '#f59e0b',
          high: '#ef4444',
          critical: '#dc2626',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flow': 'flow 2s ease-in-out infinite',
      },
      keyframes: {
        flow: {
          '0%, 100%': { strokeDashoffset: '0' },
          '50%': { strokeDashoffset: '20' },
        },
      },
    },
  },
  plugins: [],
}
