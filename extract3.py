import re
import os

transcript_path = r"C:\Users\vedan\.gemini\antigravity\brain\84124408-6389-4d44-bc40-46377d91ccb3\.system_generated\logs\transcript_full.jsonl"
out_dir = r"C:\Users\vedan\.gemini\antigravity\scratch\disasterlens"

with open(transcript_path, "r", encoding="utf-8") as f:
    text = f.read()

html_start = text.find("<!DOCTYPE html>")
html_end = text.find("</html>", html_start) + 7
html = text[html_start:html_end]

css_start = text.find("/* ==========================================================================\\n   DISASTERLENS", html_end)
if css_start == -1:
    css_start = text.find("/* ==========================================================================", html_end)

js_start = text.find("function initCommandCenterMap()")

if css_start != -1 and js_start != -1:
    css = text[css_start:js_start].strip()
    # The newlines in jsonl are escaped as \n, so we need to decode them
    css = css.replace("\\n", "\n").replace('\\"', '"').replace("\\t", "\t")
else:
    css = ""

html = html.replace("\\n", "\n").replace('\\"', '"').replace("\\t", "\t")

with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as html_f:
    html_f.write(html)

with open(os.path.join(out_dir, "style.css"), "w", encoding="utf-8") as css_f:
    css_f.write(css)

print(f"HTML size: {len(html)}")
print(f"CSS size: {len(css)}")
