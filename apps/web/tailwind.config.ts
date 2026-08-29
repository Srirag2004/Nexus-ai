import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b1620",
        panel: "#12222e",
        border: "#28404f",
        text: "#edf7f5",
        muted: "#9bb0b8",
        accent: "#b8f36b",
      },
    },
  },
  plugins: [],
};

export default config;
