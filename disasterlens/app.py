import base64
import json
import os
from typing import List

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware

import db
import inference

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Altered to prevent failing if actual checkpoint missing - since we are stubbing
MODEL_CHECKPOINT = os.environ.get(
    "MODEL_CHECKPOINT",
    os.path.join(
        BASE_DIR,
        "dummy_checkpoint.pt",
    ),
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="DER-01 Disaster & Emergency Response AI",
    description="AI-powered disaster detection and emergency response system",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL MODEL
# ============================================================

model = None


# ============================================================
# WEBSOCKET MANAGER
# ============================================================

class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):

        dead = []

        for connection in self.active_connections:

            try:
                await connection.send_text(
                    json.dumps(message)
                )

            except Exception:
                dead.append(connection)

        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()


# ============================================================
# SEVERITY LOGIC
# ============================================================

def calculate_severity(confidence):

    if confidence >= 0.80:
        return "high"

    if confidence >= 0.60:
        return "medium"

    return "low"


def severity_distribution(hazard_distribution):

    total = sum(hazard_distribution.values())

    if total <= 0:
        return {
            "low": 1.0,
            "medium": 0.0,
            "high": 0.0,
        }

    confidence = max(hazard_distribution.values())

    high = min(confidence, 1.0)
    medium = max(0.0, 1.0 - confidence)
    low = 0.0

    return {
        "low": low,
        "medium": medium,
        "high": high,
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def load_model():

    global model

    print("=" * 60)
    print("DER-01 STARTING")
    print("=" * 60)

    # Note: Using stub model without enforcing checkpoint exists
    model = inference.DisasterModel(
        MODEL_CHECKPOINT
    )

    db.init_db()

    print("[startup] Database initialized.")
    print("[startup] DER-01 ready.")
    print("=" * 60)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "DER-01 Disaster & Emergency Response AI",
        "model_loaded": model is not None,
        "classes": model.classes if model else None,
        "device": str(model.device) if model else None,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    if model is None:

        return {
            "status": "ok",
            "model_loaded": False,
            "classes": None,
            "device": None,
        }

    return {
        "status": "ok",
        "model_loaded": True,
        "classes": model.classes,
        "device": str(model.device),
    }


# ============================================================
# SUBMIT REPORT
# ============================================================

@app.post("/submit")
async def submit_report(
    file: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...),
):

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="AI model is not loaded.",
        )

    if not file.content_type or not file.content_type.startswith("image/"):

        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image.",
        )

    image_bytes = await file.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Empty image file.",
        )

    try:

        prediction = model.predict(
            image_bytes
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Could not process image: {e}",
        )

    # --------------------------------------------------------
    # Calculate severity
    # --------------------------------------------------------

    confidence = prediction[
        "hazard_confidence"
    ]

    severity = calculate_severity(
        confidence
    )

    severity_distribution_data = severity_distribution(
        prediction["hazard_distribution"]
    )

    # --------------------------------------------------------
    # Convert image to Base64
    # --------------------------------------------------------

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    # --------------------------------------------------------
    # Save database report
    # --------------------------------------------------------

    report_id = db.insert_report(
        lat,
        lon,
        prediction,
        image_base64,
    )

    # --------------------------------------------------------
    # Complete report
    # --------------------------------------------------------

    report = {

        "id": report_id,

        "lat": lat,

        "lon": lon,

        "hazard_type":
            prediction["hazard_type"],

        "hazard_confidence":
            prediction["hazard_confidence"],

        "hazard_distribution":
            prediction["hazard_distribution"],

        "priority":
            prediction["priority"],

        "recommended_action":
            prediction["recommended_action"],

        "alert":
            prediction["alert"],

        "severity":
            severity,

        "severity_distribution":
            severity_distribution_data,

        "image_base64":
            image_base64,

        "created_at":
            __import__('datetime').datetime.utcnow().isoformat() + "Z",
    }

    # --------------------------------------------------------
    # Broadcast to connected browsers
    # --------------------------------------------------------

    await manager.broadcast(
        {
            "type": "new_report",
            "report": report,
        }
    )

    return report


# ============================================================
# GET ALL REPORTS
# ============================================================

@app.get("/reports")
def get_reports():

    reports = db.list_reports()

    for report in reports:

        confidence = report[
            "hazard_confidence"
        ]

        report["severity"] = calculate_severity(
            confidence
        )

        report["severity_distribution"] = severity_distribution(
            report["hazard_distribution"]
        )

        report["priority"] = (
            "HIGH"
            if confidence >= 0.80
            else "MEDIUM"
            if confidence >= 0.60
            else "LOW"
        )

    return reports


# ============================================================
# WEBSOCKET
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )
