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
            "on-primary-container": "rgb(var(--color-on-primary-container) / <alpha-value>)",
            "primary": "rgb(var(--color-primary) / <alpha-value>)",
            "surface-variant": "rgb(var(--color-surface-variant) / <alpha-value>)",
            "inverse-on-surface": "rgb(var(--color-inverse-on-surface) / <alpha-value>)",
            "surface": "rgb(var(--color-surface) / <alpha-value>)",
            "surface-dim": "rgb(var(--color-surface-dim) / <alpha-value>)",
            "surface-container": "rgb(var(--color-surface-container) / <alpha-value>)",
            "on-tertiary-container": "rgb(var(--color-on-tertiary-container) / <alpha-value>)",
            "on-primary-fixed": "rgb(var(--color-on-primary-fixed) / <alpha-value>)",
            "background": "rgb(var(--color-background) / <alpha-value>)",
            "tertiary-container": "rgb(var(--color-tertiary-container) / <alpha-value>)",
            "surface-container-high": "rgb(var(--color-surface-container-high) / <alpha-value>)",
            "primary-fixed": "rgb(var(--color-primary-fixed) / <alpha-value>)",
            "on-surface": "rgb(var(--color-on-surface) / <alpha-value>)",
            "on-background": "rgb(var(--color-on-background) / <alpha-value>)",
            "outline-variant": "rgb(var(--color-outline-variant) / <alpha-value>)",
            "outline": "rgb(var(--color-outline) / <alpha-value>)",
            "tertiary": "rgb(var(--color-tertiary) / <alpha-value>)",
            "on-tertiary-fixed-variant": "rgb(var(--color-on-tertiary-fixed-variant) / <alpha-value>)",
            "on-secondary-fixed-variant": "rgb(var(--color-on-secondary-fixed-variant) / <alpha-value>)",
            "on-tertiary": "rgb(var(--color-on-tertiary) / <alpha-value>)",
            "surface-container-low": "rgb(var(--color-surface-container-low) / <alpha-value>)",
            "on-error-container": "rgb(var(--color-on-error-container) / <alpha-value>)",
            "error-container": "rgb(var(--color-error-container) / <alpha-value>)",
            "tertiary-fixed-dim": "rgb(var(--color-tertiary-fixed-dim) / <alpha-value>)",
            "surface-container-lowest": "rgb(var(--color-surface-container-lowest) / <alpha-value>)",
            "on-secondary-fixed": "rgb(var(--color-on-secondary-fixed) / <alpha-value>)",
            "secondary-fixed-dim": "rgb(var(--color-secondary-fixed-dim) / <alpha-value>)",
            "on-tertiary-fixed": "rgb(var(--color-on-tertiary-fixed) / <alpha-value>)",
            "on-surface-variant": "rgb(var(--color-on-surface-variant) / <alpha-value>)",
            "inverse-primary": "rgb(var(--color-inverse-primary) / <alpha-value>)",
            "primary-fixed-dim": "rgb(var(--color-primary-fixed-dim) / <alpha-value>)",
            "inverse-surface": "rgb(var(--color-inverse-surface) / <alpha-value>)",
            "tertiary-fixed": "rgb(var(--color-tertiary-fixed) / <alpha-value>)",
            "on-primary": "rgb(var(--color-on-primary) / <alpha-value>)",
            "on-primary-fixed-variant": "rgb(var(--color-on-primary-fixed-variant) / <alpha-value>)",
            "surface-tint": "rgb(var(--color-surface-tint) / <alpha-value>)",
            "error": "rgb(var(--color-error) / <alpha-value>)",
            "primary-container": "rgb(var(--color-primary-container) / <alpha-value>)",
            "on-secondary-container": "rgb(var(--color-on-secondary-container) / <alpha-value>)",
            "surface-container-highest": "rgb(var(--color-surface-container-highest) / <alpha-value>)",
            "surface-bright": "rgb(var(--color-surface-bright) / <alpha-value>)",
            "secondary-fixed": "rgb(var(--color-secondary-fixed) / <alpha-value>)",
            "on-secondary": "rgb(var(--color-on-secondary) / <alpha-value>)",
            "secondary-container": "rgb(var(--color-secondary-container) / <alpha-value>)",
            "on-error": "rgb(var(--color-on-error) / <alpha-value>)",
            "secondary": "rgb(var(--color-secondary) / <alpha-value>)"
},
        "borderRadius": {
            "DEFAULT": "0.5rem",
            "lg": "1rem",
            "xl": "1.5rem",
            "full": "9999px"
        },
        "fontFamily": {
            // Legacy names — still used by not-yet-migrated screens. Remove once
            // every surface is on the design-system faces below.
            "headline": ["Literata", "serif"],
            "body": ["Nunito Sans", "sans-serif"],
            "label": ["Nunito Sans", "sans-serif"],
            // Design system ("Warm Editorial"): a dramatic display serif, a newsy
            // text serif, and a terminal mono that also carries UI/label duty.
            "display": ["Instrument Serif", "Georgia", "Times New Roman", "serif"],
            "reader": ["Newsreader", "Georgia", "Times New Roman", "serif"],
            "mono": ["Spline Sans Mono", "ui-monospace", "SF Mono", "Menlo", "monospace"]
        }
    }
  },
  plugins: [],
};
