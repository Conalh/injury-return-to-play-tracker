import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#17201d",
        field: "#f6f7f4",
        pine: "#245142",
        rust: "#a94f2c",
        gold: "#c89a32",
        mist: "#dce7e2",
      },
      boxShadow: {
        panel: "0 10px 30px rgba(23, 32, 29, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
