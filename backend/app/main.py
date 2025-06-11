# backend/app/main.py - CORRECTED VERSION
"""
FastAPI main application for PowerBI Agent
Fixed static file serving for subpath deployment
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

# Initialize FastAPI app with root_path for subpath deployment
app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0",
    root_path="/talk4finance"  # CRITICAL: This tells FastAPI about the subpath
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local development frontend
        "http://localhost:3001",           # Docker mapped port
        "http://localhost:3002",           # Docker mapped port
        "http://127.0.0.1:3000",          # Alternative localhost
        "http://127.0.0.1:3001",          # Alternative localhost with mapped port
        "http://0.0.0.0:3000",            # Docker internal
        "http://0.0.0.0:3001",            # Docker internal mapped
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
    """Initialize database on startup"""
    print("🚀 Starting up Talk4Finance API...")
    await init_db()
    print("✅ Database initialized successfully")

    # Debug static files
    static_dir = "/app/static"
    if os.path.exists(static_dir):
        print(f"📁 Static directory contents: {os.listdir(static_dir)}")

        react_static_dir = os.path.join(static_dir, "static")
        if os.path.exists(react_static_dir):
            print(f"📁 React static directory contents: {os.listdir(react_static_dir)}")

            js_dir = os.path.join(react_static_dir, "js")
            if os.path.exists(js_dir):
                js_files = os.listdir(js_dir)
                print(f"📁 JS files: {js_files}")
                # Check first JS file content
                if js_files:
                    js_file_path = os.path.join(js_dir, js_files[0])
                    with open(js_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_line = f.readline().strip()
                        print(f"🔍 First line of {js_files[0]}: {first_line[:100]}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API"}

# API info endpoint
@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# CORS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# CRITICAL: Mount static files BEFORE defining any other routes
static_dir = "/app/static"
if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    # React puts built files in /app/static/static/ subdirectory
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        # Mount ONLY the React static files, not the whole directory
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
    else:
        print(f"❌ React static subdirectory not found at: {react_static_dir}")
        print(f"🔄 Attempting to mount main static directory: {static_dir}")
        app.mount("/static", StaticFiles(directory=static_dir), name="main_static")
else:
    print(f"❌ Static directory not found: {static_dir}")

# Handle individual assets that are in the root of static
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

# IMPORTANT: This catch-all route must be LAST
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve React app for all routes that don't match API endpoints or static files.
    This enables React Router to handle client-side routing.
    """
    print(f"🔍 Catch-all route hit for: {full_path}")

    # DO NOT serve index.html for API routes, docs, websockets, or static files
    if any(full_path.startswith(prefix) for prefix in [
        "api/", "ws/", "health", "docs", "openapi.json", "redoc", "static/"
    ]):
        print(f"❌ Should not reach catch-all: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Not found: {full_path}"})

    # Serve React index.html for all other routes (React Router will handle routing)
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for route: {full_path}")
        return FileResponse(index_path)
    else:
        print(f"❌ React index.html not found at: {index_path}")
        static_contents = os.listdir("/app/static") if os.path.exists("/app/static") else []
        return JSONResponse(
            status_code=500,
            content={
                "error": "React build not found",
                "static_exists": os.path.exists("/app/static"),
                "static_contents": static_contents
            }
        )

if __name__ == "__main__":
    print("🚀 Starting Talk4Finance API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")