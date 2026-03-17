/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0D0D0D",
        surface: "#161616",
        accent: "#FF6B00",
        secondary: "#00C2A8",
        drop: "#00E676",
        increase: "#FF1744",
        textPrimary: "#EAEAEA",
        textSecondary: "#8A8A8A",
      },
      fontFamily: {
        sans: ['Inter', 'Space Grotesk', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
