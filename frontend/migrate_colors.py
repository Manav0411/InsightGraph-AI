import json
import re

tailwind_path = "tailwind.config.js"
globals_path = "src/app/globals.css"

with open(tailwind_path, "r") as f:
    tailwind_content = f.read()

# Extract colors object using regex
colors_match = re.search(r'"colors":\s*({[^}]+})', tailwind_content)
colors_json = colors_match.group(1)

colors_dict = json.loads(colors_json)

# Generate CSS variables for :root
css_root = ":root {\n"
for key, val in colors_dict.items():
    css_root += f"  --color-{key}: {val};\n"
css_root += "}\n"

# Generate CSS variables for .dark
# We will construct a bespoke dark theme.
# Primary stays similar but brighter for dark mode: #8ecf9e
# Surface goes from #faf6f0 to #121413
css_dark = "\n.dark {\n"
css_dark += "  --color-primary: #8ecf9e;\n"
css_dark += "  --color-on-primary: #00391c;\n"
css_dark += "  --color-primary-container: #2a6038;\n"
css_dark += "  --color-on-primary-container: #d8f0de;\n"
css_dark += "  --color-surface: #121413;\n"
css_dark += "  --color-on-surface: #e4e0d8;\n"
css_dark += "  --color-surface-variant: #4a4e4a;\n"
css_dark += "  --color-on-surface-variant: #c4c8bc;\n"
css_dark += "  --color-surface-container-low: #1a1c1b;\n"
css_dark += "  --color-surface-container: #1e201f;\n"
css_dark += "  --color-surface-container-high: #2b2d2c;\n"
css_dark += "  --color-surface-container-highest: #363837;\n"
css_dark += "  --color-outline: #8c9186;\n"
css_dark += "  --color-outline-variant: #4a4e4a;\n"
css_dark += "  --color-background: #121413;\n"
css_dark += "  --color-on-background: #e4e0d8;\n"
css_dark += "  --color-secondary: #d4ccbf;\n"
css_dark += "  --color-on-secondary: #3b352b;\n"
css_dark += "  --color-secondary-container: #524b41;\n"
css_dark += "  --color-on-secondary-container: #f0e8db;\n"
css_dark += "  --color-tertiary: #dcc48e;\n"
css_dark += "  --color-on-tertiary: #3e2e04;\n"
css_dark += "  --color-tertiary-container: #574419;\n"
css_dark += "  --color-on-tertiary-container: #f8e0a8;\n"
css_dark += "  --color-error: #ffb4ab;\n"
css_dark += "  --color-on-error: #690005;\n"
css_dark += "  --color-error-container: #93000a;\n"
css_dark += "  --color-on-error-container: #ffdad8;\n"
css_dark += "}\n"

# Rewrite tailwind.config.js colors
new_colors_dict = {key: f"var(--color-{key})" for key in colors_dict}
new_colors_json = json.dumps(new_colors_dict, indent=12)
new_tailwind_content = tailwind_content.replace(colors_json, new_colors_json)

with open(tailwind_path, "w") as f:
    f.write(new_tailwind_content)

# Append to globals.css
with open(globals_path, "a") as f:
    f.write("\n" + css_root + css_dark)

print("Migration completed.")
