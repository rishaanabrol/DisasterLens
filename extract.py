import json
import os

transcript_path = r"C:\Users\vedan\.gemini\antigravity\brain\84124408-6389-4d44-bc40-46377d91ccb3\.system_generated\logs\transcript_full.jsonl"
out_dir = r"C:\Users\vedan\.gemini\antigravity\scratch\disasterlens"

user_content = ""
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            # Append if there are multiple parts, or just overwrite with latest
            # The original code just took the latest content, which might have been a small prompt if there were multiple.
            # But there's only one user prompt with this large text.
            content = data.get("content", "")
            if "<!DOCTYPE html>" in content:
                user_content = content

if not user_content:
    print("Could not find user content containing HTML.")
    exit(1)

html_start = user_content.find("<!DOCTYPE html>")
html_end = user_content.find("</html>") + 7
html = user_content[html_start:html_end]

css_start = user_content.find("/* ==========================================================================", html_end)
js_start = user_content.find("function initCommandCenterMap()")
css = user_content[css_start:js_start].strip()

# Add the Leaflet fix to CSS if it wasn't caught
if "Fix Leaflet Map Controls for Dark Mode" not in css:
    css_fix_start = user_content.find("/* Fix Leaflet Map Controls for Dark Mode */")
    if css_fix_start != -1 and css_fix_start < js_start:
        css = user_content[css_start:css_fix_start].strip() + "\n" + user_content[css_fix_start:js_start].strip()

js_raw = user_content[js_start:].strip()

app_js = """// --- Leaflet Map Integration ---
const COMMAND_MAP_INCIDENTS = [
  { lat: 37.7749, lng: -122.4194, type: "Structural Damage", severity: "High", location: "Downtown SF" },
  { lat: 37.7849, lng: -122.4094, type: "Fire", severity: "Med", location: "SOMA" },
  { lat: 37.7649, lng: -122.4294, type: "Flood", severity: "Low", location: "Mission District" },
  { lat: 37.7949, lng: -122.3994, type: "Structural Damage", severity: "High", location: "Financial District" },
  { lat: 37.7549, lng: -122.4394, type: "Fire", severity: "High", location: "Castro" },
  { lat: 37.7449, lng: -122.4194, type: "Flood", severity: "Med", location: "Bernal Heights" }
];

let commandMap, reportMiniMap, reportMiniMarker;

""" + js_raw + """

// --- UI Helpers & Init ---
function openReportModal() { document.getElementById("report-damage-modal")?.classList.add("active"); }
function closeReportModal() { document.getElementById("report-damage-modal")?.classList.remove("active"); }
function openJudgeModal() { document.getElementById("judge-drawer")?.classList.add("open"); }
function closeJudgeModal() { document.getElementById("judge-drawer")?.classList.remove("open"); }
function switchHudCase(idx) { console.log("HUD Case", idx); }
function runSimDemo(type) { console.log("Sim demo", type); }
function refreshDeviceLocation() { console.log("GPS..."); }

document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== 'undefined') lucide.createIcons();
  
  // Initialize the maps depending on which container is in the page
  if (document.getElementById("command-center-map")) initCommandCenterMap();
  if (document.getElementById("response-leaflet-map")) initLeafletLandingMap();
  if (document.getElementById("report-mini-map")) initOrUpdateReportMiniMap(37.7749, -122.4194);
  
  const clockEl = document.getElementById('utc-clock');
  if (clockEl) {
    setInterval(() => {
      const now = new Date();
      clockEl.textContent = now.toISOString().split('T')[1].split('.')[0] + ' UTC';
    }, 1000);
  }
});
"""

with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
with open(os.path.join(out_dir, "style.css"), "w", encoding="utf-8") as f:
    f.write(css)
with open(os.path.join(out_dir, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)

print("Files created successfully in", out_dir)
