import json
import os

transcript_path = r"C:\Users\vedan\.gemini\antigravity\brain\84124408-6389-4d44-bc40-46377d91ccb3\.system_generated\logs\transcript_full.jsonl"
out_dir = r"C:\Users\vedan\.gemini\antigravity\scratch\disasterlens"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "<!DOCTYPE html>" in content:
                # We found the correct message
                html_start = content.find("<!DOCTYPE html>")
                html_end = content.find("</html>") + 7
                html = content[html_start:html_end]
                
                with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as html_f:
                    html_f.write(html)
                
                # CSS
                css_marker = "/* ==========================================================================\n   DISASTERLENS — COMPLETE DESIGN SYSTEM"
                css_start = content.find(css_marker)
                if css_start == -1:
                    css_marker = "/* =========================================================================="
                    css_start = content.find(css_marker, html_end)
                    
                if css_start != -1:
                    js_start = content.find("function initCommandCenterMap()")
                    css = content[css_start:js_start].strip()
                    
                    if "Fix Leaflet Map Controls for Dark Mode" not in css:
                        css_fix_start = content.find("/* Fix Leaflet Map Controls for Dark Mode */")
                        if css_fix_start != -1 and css_fix_start < js_start:
                            css = content[css_start:css_fix_start].strip() + "\n" + content[css_fix_start:js_start].strip()

                    with open(os.path.join(out_dir, "style.css"), "w", encoding="utf-8") as css_f:
                        css_f.write(css)
                print("Extracted successfully.")
                break
