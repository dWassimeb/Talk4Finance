# backend/app/main.py - FINAL WORKING VERSION
"""
FastAPI main application for PowerBI Agent
Fixed path resolution for Docker deployment with subpath
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

# Initialize FastAPI app WITHOUT root_path (nginx strips the prefix)
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
        "https://castor.iagen-ov.fr",
        "https://castor.iagen-ov.fr/talk4finance",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API"}

# API info endpoint
@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# Debug endpoint to inspect static files
@app.get("/debug/static")
async def debug_static_files():
    """Debug endpoint to see static file structure"""
    debug_info = {"static_dir_exists": os.path.exists("/app/static")}

    if os.path.exists("/app/static"):
        debug_info["static_contents"] = os.listdir("/app/static")

        if os.path.exists("/app/static/static"):
            debug_info["nested_static_contents"] = os.listdir("/app/static/static")

            # Check JS and CSS directories
            if os.path.exists("/app/static/static/js"):
                debug_info["js_files"] = os.listdir("/app/static/static/js")
            if os.path.exists("/app/static/static/css"):
                debug_info["css_files"] = os.listdir("/app/static/static/css")

    return debug_info

# STATIC FILE MOUNTING - CRITICAL: This must be BEFORE catch-all routes
static_dir = "/app/static"
if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    # React puts built files in nested static subdirectory
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        # Mount React's nested static files
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
    else:
        print(f"❌ React static subdirectory not found, mounting main static")
        app.mount("/static", StaticFiles(directory=static_dir), name="main_static")
else:
    print(f"❌ Static directory not found: {static_dir}")

# CORS preflight handlers
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Specific asset routes for better handling
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

@app.get("/asset-manifest.json")
async def asset_manifest():
    asset_manifest_path = "/app/static/asset-manifest.json"
    if os.path.exists(asset_manifest_path):
        return FileResponse(asset_manifest_path)
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

# IMPORTANT: This catch-all route must be LAST
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve React app for all routes that don't match API endpoints.
    This handles the SPA routing and static assets correctly.
    """
    print(f"🔍 Catch-all route hit for: {full_path}")

    # Skip API routes, docs, websockets, and already mounted static files
    if any(full_path.startswith(prefix) for prefix in [
        "api/", "ws/", "health", "docs", "openapi.json", "redoc", "static/", "debug/"
    ]):
        print(f"❌ API/Static route should not reach catch-all: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Not found: {full_path}"})

    # Handle specific asset files that might not be caught by static mounting
    if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
        print(f"🔍 Asset file requested: {full_path}")

        # FIXED: Remove the talk4finance prefix correctly
        clean_path = full_path
        if full_path.startswith("talk4finance/"):
            clean_path = full_path[len("talk4finance/"):]
            print(f"🔧 Cleaned path: {clean_path}")

        # Try different possible locations for the asset
        possible_paths = []

        # For static assets (JS/CSS files)
        if clean_path.startswith("static/"):
            static_file = clean_path[len("static/"):]  # Remove "static/" prefix
            possible_paths = [
                f"/app/static/static/{static_file}",    # React nested: /app/static/static/js/main.js
                f"/app/static/{static_file}",           # Direct: /app/static/js/main.js
            ]
        else:
            # For root assets (favicon, manifest, etc.)
            possible_paths = [
                f"/app/static/{clean_path}",            # Direct path
            ]

        print(f"🔍 Trying paths: {possible_paths}")

        for asset_path in possible_paths:
            if os.path.exists(asset_path):
                print(f"✅ Found asset at: {asset_path}")
                return FileResponse(asset_path)

        # Asset not found, return 404
        print(f"❌ Asset not found: {full_path}")
        # Debug info
        if os.path.exists("/app/static"):
            print(f"📁 Static directory contents: {os.listdir('/app/static')}")
            if os.path.exists("/app/static/static"):
                print(f"📁 Nested static directory contents: {os.listdir('/app/static/static')}")

        return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

    # For all other routes (SPA routing), serve React index.html
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for route: {full_path}")
        return FileResponse(index_path)
    else:
        print(f"❌ React index.html not found at: {index_path}")

        # Debug info
        static_contents = []
        if os.path.exists("/app/static"):
            static_contents = os.listdir("/app/static")

        return JSONResponse(
            status_code=500,
            content={
                "error": "React build not found",
                "path": index_path,
                "static_exists": os.path.exists("/app/static"),
                "static_contents": static_contents,
                "requested_path": full_path
            }
        )

if __name__ == "__main__":
    print("🚀 Starting Talk4Finance API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")