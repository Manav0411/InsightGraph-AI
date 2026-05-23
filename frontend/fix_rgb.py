import re
import os

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 3:
        hex_code = ''.join([c*2 for c in hex_code])
    return f"{int(hex_code[0:2], 16)} {int(hex_code[2:4], 16)} {int(hex_code[4:6], 16)}"

# 1. Update globals.css
globals_path = "src/app/globals.css"
with open(globals_path, "r") as f:
    content = f.read()

def replace_hex(match):
    hex_code = match.group(1)
    rgb = hex_to_rgb(hex_code)
    return f": {rgb};"

new_content = re.sub(r':\s*(#[0-9a-fA-F]{3,6})\s*;', replace_hex, content)

with open(globals_path, "w") as f:
    f.write(new_content)

# 2. Update tailwind.config.js
tailwind_path = "tailwind.config.js"
with open(tailwind_path, "r") as f:
    tw_content = f.read()

def replace_var(match):
    var_name = match.group(1)
    return f'"rgb(var({var_name}) / <alpha-value>)"'

new_tw_content = re.sub(r'"(var\(--color-[^)]+\))"', replace_var, tw_content)

with open(tailwind_path, "w") as f:
    f.write(new_tw_content)

print("RGB fix applied successfully.")
