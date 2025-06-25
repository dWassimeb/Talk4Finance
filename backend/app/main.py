# backend/app/main.py - FINAL WORKING VERSION
"""
FastAPI main application for PowerBI Agent
FINAL VERSION - Working static files + properly registered API routes
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from typing import Dict, List
import asyncio

# Import routers and dependencies
from app.auth.routes import auth_router
from app.chat.routes import chat_router
from app.auth.dependencies import get_current_user
from app.database.connection import init_db
from app.chat.services import ChatService
from app.core.config import settings

# Initialize FastAPI app - NO root_path for reverse proxy
app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0"
)

print("🚀 Starting Talk4Finance API...")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://castor.iagen-ov.fr",
        "http://castor.iagen-ov.fr/talk4finance",
        "https://castor.iagen-ov.fr",
        "https://castor.iagen-ov.fr/talk4finance",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CRITICAL: Include routers BEFORE any other routes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
print("✅ API routers registered")

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            chat_service = ChatService()
            response = await chat_service.process_message(
                user_id=user_id,
                message=message_data.get("message", ""),
                conversation_id=message_data.get("conversation_id")
            )

            await manager.send_personal_message(json.dumps(response), user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up Talk4Finance API...")
    await init_db()
    print("✅ Database initialized successfully")

# Essential routes - BEFORE static mounting
@app.get("/health")
async def health_check():
    print("💚 Health check called")
    return {"status": "healthy", "service": "Talk4Finance API"}

@app.get("/api")
async def api_info():
    print("📋 API info called")
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# CORS preflight handler - BEFORE static mounting
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# STATIC FILE HANDLING - WORKING VERSION
static_dir = "/app/static"

if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    # Mount React's nested static files (CSS/JS) at /static
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")

    # Mount main static directory for other assets at /assets
    app.mount("/assets", StaticFiles(directory=static_dir), name="main_static")
    print(f"✅ Mounted main static directory: {static_dir}")
else:
    print(f"❌ Static directory not found: {static_dir}")

# Specific routes for common files - BEFORE catch-all
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

@app.get("/manifest.json")
async def manifest():
    manifest_path = "/app/static/manifest.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

@app.get("/asset-manifest.json")
async def asset_manifest():
    asset_manifest_path = "/app/static/asset-manifest.json"
    if os.path.exists(asset_manifest_path):
        return FileResponse(asset_manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

# FINAL CATCH-ALL ROUTE - MUST BE LAST
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    """
    Serve React app for all unmatched routes.
    This catches everything not handled by API routers or static mounts.
    """
    print(f"🔍 Catch-all hit: {full_path}")

    # If an API route reaches here, the routers failed to catch it
    if any(full_path.startswith(prefix) for prefix in ["api/", "ws/"]):
        print(f"❌ ERROR: API route reached catch-all: {full_path}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "API route not found",
                "path": full_path,
                "message": "This API endpoint does not exist"
            }
        )

    # Handle static asset requests that weren't caught by mounts
    if any(full_path.endswith(ext) for ext in ['.js', '.css', '.map', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.json']):
        print(f"🔍 Static asset requested: {full_path}")

        # Clean up the path
        cleaned_path = full_path
        if cleaned_path.startswith('/'):
            cleaned_path = cleaned_path[1:]
        if cleaned_path.startswith('talk4finance/'):
            cleaned_path = cleaned_path[13:]

        print(f"🔧 Cleaned path: {cleaned_path}")

        # Try different possible paths for the asset
        possible_paths = [
            f"/app/static/{cleaned_path}",
            f"/app/static/static/{cleaned_path}",  # React puts CSS/JS in nested static
        ]

        # If it's a static/* path, try the nested structure
        if cleaned_path.startswith('static/'):
            asset_path = cleaned_path[7:]  # Remove 'static/' prefix
            possible_paths.append(f"/app/static/static/{asset_path}")

        print(f"🔍 Trying asset paths: {possible_paths}")

        for file_path in possible_paths:
            if os.path.exists(file_path):
                print(f"✅ Found asset at: {file_path}")

                # Determine correct media type
                media_type = "text/plain"
                if file_path.endswith('.js'):
                    media_type = "application/javascript"
                elif file_path.endswith('.css'):
                    media_type = "text/css"
                elif file_path.endswith('.json'):
                    media_type = "application/json"
                elif file_path.endswith('.ico'):
                    media_type = "image/x-icon"
                elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    media_type = "image/*"
                elif file_path.endswith('.svg'):
                    media_type = "image/svg+xml"

                return FileResponse(file_path, media_type=media_type)

        print(f"❌ Asset not found: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

    # For all other routes, serve React index.html (SPA routing)
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for: {full_path}")
        return FileResponse(index_path, media_type="text/html")
    else:
        print(f"❌ React index.html not found at: {index_path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "React build not found",
                "index_path": index_path,
                "requested_path": full_path
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)