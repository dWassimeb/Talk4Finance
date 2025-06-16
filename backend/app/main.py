# backend/app/main.py - FOR proxy_pass http://10.8.20.232:3001/
"""
FastAPI main application for PowerBI Agent
For nginx config: proxy_pass http://10.8.20.232:3001/
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from typing import Dict, List
import asyncio

from app.auth.routes import auth_router
from app.chat.routes import chat_router
from app.auth.dependencies import get_current_user
from app.database.connection import init_db
from app.chat.services import ChatService
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://31.44.217.0",
        "http://31.44.217.0/talk4finance",
        "http://castor.iagen-ov.fr",
        "http://castor.iagen-ov.fr/talk4finance",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers (nginx strips /talk4finance, backend gets /api/auth)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

manager = ConnectionManager()

# WebSocket endpoint (nginx strips /talk4finance, so backend gets /ws)
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    chat_service = ChatService()
    # ... websocket implementation

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API"}

# API info endpoint
@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# Mount static files (nginx strips /talk4finance, backend gets /static)
static_dir = "/app/static"
if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
    else:
        print(f"❌ React static subdirectory not found")
        app.mount("/static", StaticFiles(directory=static_dir), name="main_static")
else:
    print(f"❌ Static directory not found: {static_dir}")

# CORS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Catch-all route for React SPA (nginx strips /talk4finance)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve React app for all routes that don't match API endpoints or static files.
    """
    print(f"🔍 Catch-all route hit for: {full_path}")

    # Skip API routes, docs, websockets, and static files
    if any(full_path.startswith(prefix) for prefix in [
        "api/", "ws/", "health", "docs", "openapi.json", "redoc", "static/"
    ]):
        print(f"❌ API/Static route should not reach catch-all: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Not found: {full_path}"})

    # Handle asset files
    if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
        print(f"🔍 Asset file requested: {full_path}")
        asset_path = f"/app/static/{full_path}"
        if os.path.exists(asset_path):
            return FileResponse(asset_path)
        else:
            return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

    # Serve React index.html for SPA routing
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for route: {full_path}")
        return FileResponse(index_path)
    else:
        print(f"❌ React index.html not found at: {index_path}")
        return JSONResponse(status_code=500, content={"error": "React build not found"})

if __name__ == "__main__":
    print("🚀 Starting Talk4Finance API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")