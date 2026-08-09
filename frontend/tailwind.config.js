/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7ff",
          100: "#d9edff",
          200: "#bce0ff",
          300: "#8ecdff",
          400: "#59b0ff",
          500: "#338fff",
          600: "#1d6ef5",
          700: "#1558e1",
          800: "#1848b6",
          900: "#1a408f",
          950: "#14285a",
        },
      },
    },
  },
  plugins: [],
};
