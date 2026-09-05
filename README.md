# DisasterLens

> **See the damage. Map the response.**

DisasterLens is an AI-powered disaster reporting and emergency response platform that transforms citizen-captured photographs into **geotagged, classified incident reports**.

Users can upload an image of a disaster, capture their GPS coordinates, and submit the report for automated hazard classification. Reports are stored in a SQLite database and broadcast in real time to an interactive GIS dashboard.

## Key Features

- **Disaster Image Classification**
  - Fire
  - Structural Damage
  - Flood / Water Damage
- **AI Confidence Scoring** for every classification
- **Automatic Severity Assessment**
  - Low
  - Medium
  - High
- **GPS Location Capture** using the browser Geolocation API
- **Interactive GIS Maps** powered by Leaflet
- **Live Incident Feed** with filtering by hazard and severity
- **Real-time Updates** using WebSockets
- **SQLite Database** for persistent incident storage
- **Incident Visualization** with location markers and risk zones
- **Emergency Recommendations** generated for detected hazards
- Tactical emergency-operations-style dashboard UI

## System Workflow

```text
┌─────────────────────┐
│   Citizen / User    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Upload Disaster     │
│ Photograph          │
└──────────┬──────────┘
           │
           ├──────────────► GPS Location
           │
           ▼
┌─────────────────────┐
│ AI Image Inference  │
│                     │
│ Fire                │
│ Structural Damage   │
│ Flood / Water       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Severity & Priority │
│ Assessment          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ SQLite Database     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Live GIS Dashboard  │
│ + Incident Feed     │
└─────────────────────┘
           ▲
           │
      WebSocket
      Real-time
      Updates
```

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- [Leaflet](https://leafletjs.com/) — interactive maps
- [Lucide](https://lucide.dev/) — interface icons
- OpenStreetMap
- Esri World Imagery

### Backend

- Python
- FastAPI
- Uvicorn
- WebSockets
- SQLite
- Pillow

### AI / Computer Vision

The backend contains a `DisasterModel` inference layer that processes uploaded images and returns:

- Hazard type
- Classification confidence
- Hazard probability distribution
- Priority
- Recommended action
- Alert message

> **Note:** The current repository includes a lightweight mock inference implementation rather than the trained PyTorch checkpoint referenced by the API configuration. It uses image characteristics to simulate classification and confidence values.

## Project Structure

```text
disasterlens/
│
├── index.html
├── style.css
├── app.js
│
├── app.py
├── inference.py
├── db.py
│
├── disaster.db
├── run.bat
│
├── assets/
│   ├── fire.jpg
│   ├── flood.jpg
│   ├── structural.jpg
│   ├── thumb_fire.jpg
│   ├── thumb_flood.jpg
│   ├── thumb_structure.jpg
│   ├── footer_logo.png
│   └── qr_support.png
│
└── ai model trained.py
```

## API

The FastAPI backend exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API status and model information |
| `GET` | `/health` | Health check |
| `POST` | `/submit` | Submit and classify a disaster image |
| `GET` | `/reports` | Retrieve stored incident reports |
| `WebSocket` | `/ws` | Receive real-time incident updates |

### Submit Report

`POST /submit`

Accepts:

- `file` — disaster image
- `lat` — latitude
- `lon` — longitude

The server processes the image, determines the hazard type and confidence, calculates severity, stores the report, and broadcasts the new incident through WebSockets.

## Severity Logic

Severity is currently derived from the model confidence:

```text
Confidence ≥ 0.80  → HIGH
Confidence ≥ 0.60  → MEDIUM
Confidence < 0.60  → LOW
```

## Getting Started

### Prerequisites

Make sure you have:

- Python 3.x
- A modern web browser
- pip

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/disasterlens.git
cd disasterlens/disasterlens
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn python-multipart pillow
```

### 3. Start the backend

On Windows:

```bash
run.bat
```

Or manually:

```bash
uvicorn app:app --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 4. Open the frontend

Open `index.html` in your browser.

For best results, serve it through a local development server such as VS Code Live Server.

## Database

DisasterLens uses **SQLite** to store submitted reports.

Each report contains:

- Incident ID
- Latitude
- Longitude
- Hazard type
- Confidence score
- Hazard distribution
- Priority
- Recommended action
- Alert
- Submitted image
- Timestamp

Images are currently stored as Base64 data inside the database.

## Real-Time Architecture

DisasterLens uses WebSockets to push newly submitted incidents to connected dashboards.

```text
User submits report
        ↓
FastAPI /submit
        ↓
AI inference
        ↓
SQLite storage
        ↓
WebSocket broadcast
        ↓
Connected dashboards
        ↓
Map + live incident feed update
```

This eliminates the need for the dashboard to continuously poll the server for new incidents.

## Maps & Geospatial Visualization

Leaflet is used to visualize disaster locations.

Each incident is represented using:

- Hazard-specific map markers
- Inner high-risk zones
- Outer moderate-risk zones
- Incident popups
- Coordinate tooltips
- Hazard and severity filters

Users can switch between tactical map and satellite imagery.

## Future Improvements

- Replace mock inference with the fully trained computer-vision model
- Improve classification accuracy with a larger disaster dataset
- Automated severity prediction beyond confidence thresholds
- User authentication and role-based access
- Image storage using object storage instead of Base64 in SQLite
- Push notifications for high-severity incidents
- Integration with emergency services
- Historical incident analytics
- Mobile/PWA support
- Advanced GIS heatmaps and disaster-density analysis

## Hackathon

DisasterLens was developed as a rapid-prototyping project focused on applying **AI, geospatial technology, and real-time web infrastructure to disaster response**.

The goal is simple:

> **Capture → Classify → Locate → Prioritize → Respond**

## License

This project is currently intended for educational, research, and hackathon purposes.
