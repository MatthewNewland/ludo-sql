/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{svelte,html,css,js,ts}"],
  darkMode: "class",
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
}
