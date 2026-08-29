import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#09090b",
        panel: "#111115",
        border: "#27272a",
        text: "#fafafa",
        muted: "#a1a1aa",
        accent: "#38bdf8",
      },
    },
  },
  plugins: [],
};

export default config;

