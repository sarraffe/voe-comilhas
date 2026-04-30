/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1A3A8F',
          50: '#EEF2FF',
          100: '#E0E7FF',
          500: '#1A3A8F',
          600: '#152E72',
          700: '#102358',
        },
        danger: {
          DEFAULT: '#B01E14',
          50: '#FFF1F0',
          100: '#FFE0DE',
          500: '#B01E14',
          600: '#8E1810',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
