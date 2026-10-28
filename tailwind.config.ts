import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FAFAF9",
        surface: "#FFFFFF",
        primary: {
          DEFAULT: "#EA580C", // Primary Orange
          soft: "#FFF7ED",    // Soft Orange
          light: "#FFEDD5",   // Light Orange
          hover: "#C2410C",
        },
        text: {
          primary: "#1C1917",
          secondary: "#78716C",
          muted: "#A8A29E",
        },
        border: "#E7E5E4",
        status: {
          success: "#16A34A",
          warning: "#D97706",
          error: "#DC2626",
          waiting: "#78716C",
          running: "#EA580C",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
      boxShadow: {
        subtle: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        card: "0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
