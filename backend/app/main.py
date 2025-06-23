# backend/app/main.py - CORRECT 3-ENVIRONMENT SETUP
"""
FastAPI main application for PowerBI Agent
Supports 3 deployment environments:
1. Local development (separate servers)
2. Docker Desktop (single container)
3. DocaCloud (reverse proxy)
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

from app.auth.routes import auth_router
from app.chat.routes import chat_router
from app.auth.dependencies import get_current_user
from app.database.connection import init_db
from app.chat.services import ChatService
from app.core.config import settings

# Detect if we're behind a reverse proxy
def is_reverse_proxy_env():
    """Check if we're running behind a reverse proxy (DocaCloud)"""
    return os.getenv('HTTP_X_FORWARDED_PREFIX') == '/talk4finance' or \
        os.getenv('REVERSE_PROXY') == 'true'

# Initialize FastAPI app
# For reverse proxy environments, set root_path to handle the prefix correctly
root_path = "/talk4finance" if is_reverse_proxy_env() else None

app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0",
    root_path=root_path
)

print(f"🚀 Starting FastAPI with root_path: {root_path}")
print(f"🔍 Environment detection:")
print(f"   - X-Forwarded-Prefix: {os.getenv('HTTP_X_FORWARDED_PREFIX', 'None')}")
print(f"   - REVERSE_PROXY: {os.getenv('REVERSE_PROXY', 'None')}")

# CORS middleware - Allow all necessary origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",  # For local backend testing
        "http://127.0.0.1:8000",

        # DocaCloud production
        "http://castor.iagen-ov.fr",
        "http://castor.iagen-ov.fr/talk4finance",
        "https://castor.iagen-ov.fr",
        "https://castor.iagen-ov.fr/talk4finance",

        # Additional IPs if needed
        "http://31.44.217.0",
        "http://31.44.217.0/talk4finance",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

# WebSocket endpoint for real-time chat
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

            print(f"📥 WebSocket received:")
            print(f"   - User ID: {user_id}")
            print(f"   - Message: {question}")
            print(f"   - Conversation ID: {conversation_id}")

            if question:
                # FIX: Use send_personal_message instead of send_message
                await manager.send_personal_message(
                    json.dumps({"type": "typing", "typing": True}),
                    user_id
                )

                try:
                    response = await chat_service.process_message(
                        user_id=user_id,
                        message=question,
                        conversation_id=conversation_id
                    )

                    # FIX: Use send_personal_message instead of send_message
                    await manager.send_personal_message(
                        json.dumps({"type": "message", "response": response, "typing": False}),
                        user_id
                    )

                except Exception as e:
                    print(f"❌ Error in process_message: {str(e)}")

                    # FIX: Use send_personal_message instead of send_message
                    await manager.send_personal_message(
                        json.dumps({"type": "error", "error": f"Error: {str(e)}", "typing": False}),
                        user_id
                    )

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

# Debug endpoint
@app.get("/debug/static")
async def debug_static_files():
    """Debug endpoint to see static file structure"""
    debug_info = {
        "static_dir_exists": os.path.exists("/app/static"),
        "environment": "reverse_proxy" if is_reverse_proxy_env() else "direct",
        "root_path": app.root_path
    }

    if os.path.exists("/app/static"):
        debug_info["static_contents"] = os.listdir("/app/static")
        if os.path.exists("/app/static/static"):
            debug_info["nested_static_contents"] = os.listdir("/app/static/static")

    return debug_info

# STATIC FILE MOUNTING
static_dir = "/app/static"
if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    # Mount React's nested static files (CSS/JS)
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")

    # Mount root static for favicon, manifest, etc.
    app.mount("/assets", StaticFiles(directory=static_dir), name="root_static")
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

# Specific asset routes with better path handling
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    print(f"🔍 Looking for favicon at: {favicon_path}")
    if os.path.exists(favicon_path):
        print(f"✅ Found favicon at: {favicon_path}")
        return FileResponse(favicon_path, media_type="image/x-icon")
    print(f"❌ Favicon not found at: {favicon_path}")
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

# Handle static files and React routing
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    """
    Serve React app for all routes that don't match API endpoints.
    Handles both static assets and SPA routing.
    """
    print(f"🔍 Catch-all route hit for: {full_path}")

    # Check if it's a static asset request
    if any(full_path.endswith(ext) for ext in ['.js', '.css', '.map', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.json']):
        print(f"🔍 Asset file requested: {full_path}")

        # Clean the path - remove any prefix that might be added by reverse proxy
        cleaned_path = full_path
        if cleaned_path.startswith('talk4finance/'):
            cleaned_path = cleaned_path[13:]  # Remove 'talk4finance/' prefix

        print(f"🔧 Cleaned path: {cleaned_path}")

        # Try different possible paths for the asset
        possible_paths = [
            f"/app/static/{cleaned_path}",
            f"/app/static/static/{cleaned_path}",  # React puts assets in nested static
        ]

        print(f"🔍 Trying paths: {possible_paths}")

        for file_path in possible_paths:
            if os.path.exists(file_path):
                print(f"✅ Found asset at: {file_path}")
                # Determine media type based on extension
                media_type = "text/plain"
                if file_path.endswith('.js'):
                    media_type = "application/javascript"
                elif file_path.endswith('.css'):
                    media_type = "text/css"
                elif file_path.endswith('.json'):
                    media_type = "application/json"
                elif file_path.endswith('.ico'):
                    media_type = "image/x-icon"

                return FileResponse(file_path, media_type=media_type)

        print(f"❌ Asset not found: {full_path}")
        # Debug: Show directory contents
        if os.path.exists("/app/static"):
            print(f"📁 Static directory contents: {os.listdir('/app/static')}")
            if os.path.exists("/app/static/static"):
                print(f"📁 Nested static directory contents: {os.listdir('/app/static/static')}")

        return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

    # For all other routes, serve React index.html (SPA routing)
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for route: {full_path}")
        return FileResponse(index_path, media_type="text/html")
    else:
        print(f"❌ React index.html not found at: {index_path}")
        return JSONResponse(status_code=404, content={"detail": "React app not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)