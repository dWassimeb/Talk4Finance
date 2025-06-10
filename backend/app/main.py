# backend/app/main.py - SIMPLE FIX FOR STATIC FILES
"""
FastAPI main application for PowerBI Agent
Simple fix for static file serving
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
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

# Initialize FastAPI app with subpath support
app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0",
    root_path="/talk4finance"  # This tells FastAPI it's deployed under /talk4finance
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
        "https://castor.iagen-ov.fr",
        "https://castor.iagen-ov.fr/talk4finance",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
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

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    chat_service = ChatService()

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            question = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id")

            if question:
                await manager.send_message(user_id, {"type": "typing", "typing": True})
                try:
                    response = await chat_service.process_message(
                        user_id=user_id, message=question, conversation_id=conversation_id
                    )
                    await manager.send_message(user_id, {"type": "message", "response": response, "typing": False})
                except Exception as e:
                    await manager.send_message(user_id, {"type": "error", "error": f"Error: {str(e)}", "typing": False})
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.on_event("startup")
async def startup_event():
    print("Starting up Talk4Finance API...")
    await init_db()
    print("Database initialized successfully")

    # Debug: Print static directory contents
    static_dir = "/app/static"
    if os.path.exists(static_dir):
        print(f"📁 Static directory contents: {os.listdir(static_dir)}")

        static_subdir = os.path.join(static_dir, "static")
        if os.path.exists(static_subdir):
            print(f"📁 Static/static directory contents: {os.listdir(static_subdir)}")

            js_dir = os.path.join(static_subdir, "js")
            if os.path.exists(js_dir):
                print(f"📁 JS files: {os.listdir(js_dir)}")

            css_dir = os.path.join(static_subdir, "css")
            if os.path.exists(css_dir):
                print(f"📁 CSS files: {os.listdir(css_dir)}")
    else:
        print(f"❌ Static directory not found: {static_dir}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API"}

@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# CRITICAL: Mount static files BEFORE any other routes
static_dir = "/app/static"
if os.path.exists(static_dir):
    # React build puts files in /app/static/static/ structure
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="static")
    else:
        print(f"❌ React static directory not found: {react_static_dir}")
        # Fallback: mount the main static directory
        print(f"🔄 Fallback: mounting main static directory: {static_dir}")
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"❌ No static directory found at: {static_dir}")

# Handle individual static assets
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

@app.get("/manifest.json")
async def manifest():
    manifest_path = "/app/static/manifest.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path)
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

# CORS preflight
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Catch-all route for React Router (MUST BE LAST)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all routes not handled above"""

    print(f"🔍 Catch-all route hit: {full_path}")

    # DO NOT serve index.html for static files
    if full_path.startswith("static/"):
        print(f"❌ Static file request should not reach catch-all: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Static file not found: {full_path}"})

    # DO NOT serve index.html for API routes
    if any(full_path.startswith(prefix) for prefix in ["api/", "ws/", "health", "docs", "openapi.json", "redoc"]):
        print(f"❌ API route request should not reach catch-all: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"API endpoint not found: {full_path}"})

    # Serve React index.html for all other routes
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for: {full_path}")
        return FileResponse(index_path)
    else:
        print(f"❌ React index.html not found at: {index_path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "React build not found",
                "index_path": index_path,
                "static_exists": os.path.exists("/app/static"),
                "static_contents": os.listdir("/app/static") if os.path.exists("/app/static") else []
            }
        )

if __name__ == "__main__":
    print("🚀 Starting Talk4Finance API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")