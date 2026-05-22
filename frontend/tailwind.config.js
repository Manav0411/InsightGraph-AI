/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
        "colors": {
            "on-primary-container": "#d8f0de",
            "primary": "#4a7c59",
            "surface-variant": "#e4e0d8",
            "inverse-on-surface": "#f5f0e8",
            "surface": "#faf6f0",
            "surface-dim": "#dbd7cf",
            "surface-container": "#f0ece4",
            "on-tertiary-container": "#554020",
            "on-primary-fixed": "#002110",
            "background": "#faf6f0",
            "tertiary-container": "#c4a66a",
            "surface-container-high": "#eae6de",
            "primary-fixed": "#c8e8d0",
            "on-surface": "#2e3230",
            "on-background": "#2e3230",
            "outline-variant": "#c4c8bc",
            "outline": "#74796e",
            "tertiary": "#705c30",
            "on-tertiary-fixed-variant": "#554020",
            "on-secondary-fixed-variant": "#4a4538",
            "on-tertiary": "#ffffff",
            "surface-container-low": "#f5f1ea",
            "on-error-container": "#690005",
            "error-container": "#ffdad8",
            "tertiary-fixed-dim": "#dcc48e",
            "surface-container-lowest": "#ffffff",
            "on-secondary-fixed": "#1e1a13",
            "secondary-fixed-dim": "#d4ccbf",
            "on-tertiary-fixed": "#221a05",
            "on-surface-variant": "#4a4e4a",
            "inverse-primary": "#8ecf9e",
            "primary-fixed-dim": "#8ecf9e",
            "inverse-surface": "#2e3230",
            "tertiary-fixed": "#f8e0a8",
            "on-primary": "#ffffff",
            "on-primary-fixed-variant": "#2a6038",
            "surface-tint": "#4a7c59",
            "error": "#b83230",
            "primary-container": "#78a886",
            "on-secondary-container": "#5e5548",
            "surface-container-highest": "#e4e0d8",
            "surface-bright": "#faf6f0",
            "secondary-fixed": "#f0e8db",
            "on-secondary": "#ffffff",
            "secondary-container": "#f0e8db",
            "on-error": "#ffffff",
            "secondary": "#6b6358"
        },
        "borderRadius": {
            "DEFAULT": "0.5rem",
            "lg": "1rem",
            "xl": "1.5rem",
            "full": "9999px"
        },
        "fontFamily": {
            "headline": ["Literata", "serif"],
            "body": ["Nunito Sans", "sans-serif"],
            "label": ["Nunito Sans", "sans-serif"]
        }
    }
  },
  plugins: [],
};
