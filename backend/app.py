from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from ws_server import websocket_endpoint

# ─────────────────────────────────────────
#  UNMUTE.AI — FastAPI Entry Point
# ─────────────────────────────────────────

app = FastAPI(title="UNMUTE.AI Backend")

# CORS — required for browser frontend on Windows (file:// origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────

@app.get("/")
def root():
    return {"status": "UNMUTE.AI server is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket_endpoint(websocket)