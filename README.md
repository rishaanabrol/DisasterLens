# DisasterLens — Design System & Visual Foundation

**DisasterLens** is a citizen-reported disaster damage mapping platform engineered for emergency operations centers (EOC), first responders, and municipal disaster coordination teams.

```
Capture → Locate → Classify → Map → Respond
```

---

## 🛡️ Visual Philosophy & Anti "AI Slop" Design

DisasterLens replaces generic SaaS gradients, neon glows, and AI sparkle gimmicks with a **tactical, mission-critical operations aesthetic**:

1. **Urgency without panic**: High-contrast, dark-first slate canvas (`#06080c` to `#101620`) that reduces eye strain during 24/7 command center monitoring.
2. **Technology without gimmicks**: Hairline borders (`rgba(255, 255, 255, 0.08)`), monospace telemetry telemetry data blocks, precision reticles, and sub-second classification latencies.
3. **Clarity without clutter**: Strict visual hierarchy with editorial-scale headings, compact metadata labels, and generous whitespace.
4. **Restrained color semantics**:
   - **Crimson Red (`#ef4444`)**: Reserved **strictly** for high-severity hazards and active threat alerts.
   - **Tactical Amber (`#f59e0b`)**: Medium severity and advisory warnings.
   - **Muted Yellow (`#eab308`)**: Low severity and minor structural/environmental alerts.
   - **GIS Cyan/Blue (`#38bdf8`)**: Sensor location, coordinate locks, and GIS radar sweeps.
   - **System Emerald (`#10b981`)**: Verified status, nominal system health, and satellite locks.

---

## 📐 Architecture & Core Features

### 1. Frontline Ingestion (Capture & Geotag)
- Client-side browser GPS auto-locking (`navigator.geolocation`) with accuracy confidence.
- EXIF timestamp & sensor heading extraction to prevent out-of-region spam or spoofing.

### 2. Multi-Threat Classification Engine
- **Fire**: Active flame detection, thermal smoke boundary tracking, wildland-urban interface (WUI) risk evaluation.
- **Structural Damage**: Load-bearing masonry failure, facade shear fractures, pancake collapse, roadway rubble obstructions.
- **Flood / Water Damage**: Inundation depth calculation, waterline identification, impassable corridors, submerged utilities.

### 3. Tactical Live Response Map
- Dark vector tiles powered by Leaflet.
- Custom pulsating radar pins color-coded by hazard type and severity.
- Real-time incident stream with immediate map fly-to and telemetry inspection popup.
- Multi-category filtering (`All`, `Fire`, `Structural`, `Flood`, `High Severity Only`).

### 4. Interactive Ground Triage Simulator
- Live edge AI simulation tool for judges and users.
- Test custom uploaded photos or sample disaster scenarios with sub-second scoring, confidence meters, and map broadcasting.

### 5. Judge Mode Evaluation Drawer
- Instant shortcut via keyboard `[J]` or navigation bar button.
- Comprehensive technical breakdown of problem statement, CV model pipeline, zero-trust verification, and resilience architecture.

---

## 🚀 How to Run Locally

You can open `index.html` directly in any modern web browser or serve it via Python's built-in HTTP server:

```bash
# Navigate to directory
cd C:\Users\Rishaan\.gemini\antigravity\scratch\disasterlens

# Launch local server
python -m http.server 8080
```

Then visit:
`http://localhost:8080`

---

## 🗂️ Single-Page Integrated Build — `final.html`

All five screens (Overview, Report Damage, Live Map, Damage Assessment, Judge Mode) are also packaged into **one unified site**: `final.html`. This is the recommended entry point — it hosts every module behind a shared EOC shell (telemetry bar, global nav, mobile nav, footer) and drives all five views with hash routing:

- `#/overview` — Hero HUD + operational pipeline + live grid preview
- `#/report` — Citizen intake workflow (photo upload → GPS → analysis overlay)
- `#/map` — Fullscreen command map (filters, activity feed, report drawer)
- `#/assessment` — Classification result screen (bounding boxes, gauge, forensic telemetry)
- `#/judge` — Live five-slot judge console

```bash
python -m http.server 8080
# then open -> http://localhost:8080/final.html
```

### How the integration works
- `app.js` runs in a **single-page mode** (`window.DL_SINGLE_PAGE = true`) where DOM-ready auto-init is deferred to the router. A shared `dlNav()` helper routes all in-app navigation to hash routes instead of separate `.html` files.
- Each screen's markup lives in a `<template>` block that the router lazily clones into `#app-view-root` on first visit (so Leaflet maps, the geolocation prompt, and the judge pipeline only initialize when their view actually opens).
- Leaflet map instances are re-`invalidateSize()`d on every view re-show, and the report/judge forms re-arm their state when revisited.

To host it for real, the whole folder is static — drop it on any static host or run `npx vercel` / a cloud bucket and open `final.html`.

---

## 🤖 DER-01 AI Inference Backend (hazard classification)

Photo uploads are classified by your **trained FastAPI model** (DER-01: `POST /submit`), replacing the built-in demo classifier whenever the backend is reachable.

### Wiring
- The page sends `POST {apiBaseUrl}/submit` (`multipart/form-data`: `file`, `lat`, `lon`) for every report photo.
- The returned prediction is merged into the report record and drives the drawer, **Damage Assessment** screen, and **Live Map** markers. Broadcast reports pushed by the backend's `/ws` endpoint can be ingested live on the map — call `enableLiveReports()` (or set `localStorage.dl_live_reports = 1`) to turn the WebSocket stream on.
- **If the backend is down/unreachable, the app falls back to the demo classifier** so the flow never dead-ends in a static preview. `DL_CONFIG.aiFallback`, `apiTimeoutMs`, and `apiRetries` control that behavior.

### Configure the API URL
Default is `http://127.0.0.1:8000`. Override at runtime without rebuilding:

```html
<script>window.__DL_API_BASE__ = "https://your-host.example"</script>
```

_or_ set an env var at build time: `VITE_DL_API_BASE`.

### Running DER-01
Keep the FastAPI service next to the site (or deploy it separately) — it expects `main.py`, `db.py`, `inference.py`, and the trained checkpoint at
`model_training/checkpoints/best.pt`:

```bash
# from your DER-01 backend directory
uvicorn main:app --host 0.0.0.0 --port 8000
```

Load model checkpoint path via `MODEL_CHECKPOINT` env if your model is elsewhere.
