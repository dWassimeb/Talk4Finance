# backend/app/main.py - DIAGNOSTIC VERSION
"""
Diagnostic version to identify import/dependency issues
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
import traceback

print("🔍 Starting diagnostic main.py...")

# Test imports one by one to find issues
print("📦 Testing imports...")

try:
    print("  - Testing database connection import...")
    from app.database.connection import init_db
    print("  ✅ Database connection import successful")
except Exception as e:
    print(f"  ❌ Database connection import failed: {e}")
    traceback.print_exc()

try:
    print("  - Testing config import...")
    from app.core.config import settings
    print(f"  ✅ Config import successful - secret_key: {settings.secret_key[:10]}...")
except Exception as e:
    print(f"  ❌ Config import failed: {e}")
    traceback.print_exc()

try:
    print("  - Testing auth dependencies import...")
    from app.auth.dependencies import get_current_user
    print("  ✅ Auth dependencies import successful")
except Exception as e:
    print(f"  ❌ Auth dependencies import failed: {e}")
    traceback.print_exc()

try:
    print("  - Testing auth routes import...")
    from app.auth.routes import auth_router
    print("  ✅ Auth routes import successful")
    print(f"     Auth router routes: {[route.path for route in auth_router.routes]}")
except Exception as e:
    print(f"  ❌ Auth routes import failed: {e}")
    traceback.print_exc()
    # Create a dummy router if import fails
    from fastapi import APIRouter
    auth_router = APIRouter()

    @auth_router.post("/login")
    async def dummy_login():
        return {"error": "Auth router import failed"}

    @auth_router.post("/register")
    async def dummy_register():
        return {"error": "Auth router import failed"}

try:
    print("  - Testing chat routes import...")
    from app.chat.routes import chat_router
    print("  ✅ Chat routes import successful")
except Exception as e:
    print(f"  ❌ Chat routes import failed: {e}")
    traceback.print_exc()
    # Create a dummy router if import fails
    from fastapi import APIRouter
    chat_router = APIRouter()

    @chat_router.get("/conversations")
    async def dummy_conversations():
        return {"error": "Chat router import failed"}

try:
    print("  - Testing chat services import...")
    from app.chat.services import ChatService
    print("  ✅ Chat services import successful")
except Exception as e:
    print(f"  ❌ Chat services import failed: {e}")
    traceback.print_exc()

print("📦 All imports tested!")

# Initialize FastAPI app
app = FastAPI(
    title="PowerBI Agent API - DIAGNOSTIC",
    description="Diagnostic version to identify issues",
    version="1.0.0-diagnostic"
)

print("🚀 FastAPI app created")

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

print("🔗 CORS middleware added")

# Include API routers with detailed logging
print("📡 Registering API routers...")

try:
    print("  - Registering auth router...")
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    print("  ✅ Auth router registered successfully")

    # Log auth router routes
    for route in auth_router.routes:
        print(f"     📝 Auth route: {route.methods} {route.path}")

except Exception as e:
    print(f"  ❌ Auth router registration failed: {e}")
    traceback.print_exc()

try:
    print("  - Registering chat router...")
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    print("  ✅ Chat router registered successfully")

    # Log chat router routes
    for route in chat_router.routes:
        print(f"     📝 Chat route: {route.methods} {route.path}")

except Exception as e:
    print(f"  ❌ Chat router registration failed: {e}")
    traceback.print_exc()

print("📡 Router registration complete!")

# WebSocket manager (simplified for diagnostics)
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
    print(f"🔌 WebSocket connection attempt for user: {user_id}")
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📨 WebSocket message received: {data[:100]}...")

            # Simple echo for diagnostics
            await manager.send_personal_message(f"Echo: {data}", user_id)
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for user: {user_id}")
        manager.disconnect(user_id)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up diagnostic API...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        traceback.print_exc()

# Essential routes
@app.get("/health")
async def health_check():
    print("💚 Health check called")
    return {
        "status": "healthy",
        "service": "Talk4Finance API - DIAGNOSTIC",
        "auth_router_routes": len(auth_router.routes),
        "chat_router_routes": len(chat_router.routes)
    }

@app.get("/api")
async def api_info():
    print("📋 API info called")
    return {
        "message": "PowerBI Agent API - DIAGNOSTIC",
        "version": "1.0.0-diagnostic",
        "auth_routes": [f"{route.methods} {route.path}" for route in auth_router.routes],
        "chat_routes": [f"{route.methods} {route.path}" for route in chat_router.routes]
    }

# Debug endpoint to check all registered routes
@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to see all registered routes"""
    print("🔍 Debug routes endpoint called")
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unnamed')
            })

    print(f"📊 Total routes registered: {len(routes)}")
    return {"routes": routes, "total": len(routes)}

# Test login endpoint (direct, not through router)
@app.post("/api/auth/test-login")
async def test_login():
    print("🧪 Test login endpoint called")
    return {"message": "Test login endpoint working", "status": "success"}

# CORS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    print(f"🔄 CORS preflight for: {rest_of_path}")
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Static file handling (simplified)
static_dir = "/app/static"

if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")

    app.mount("/assets", StaticFiles(directory=static_dir), name="main_static")
    print(f"✅ Mounted main static directory: {static_dir}")
else:
    print(f"❌ Static directory not found: {static_dir}")

# Specific routes for common files
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    print(f"🔍 Favicon requested: {favicon_path}")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

@app.get("/manifest.json")
async def manifest():
    manifest_path = "/app/static/manifest.json"
    print(f"🔍 Manifest requested: {manifest_path}")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

@app.get("/asset-manifest.json")
async def asset_manifest():
    asset_manifest_path = "/app/static/asset-manifest.json"
    print(f"🔍 Asset manifest requested: {asset_manifest_path}")
    if os.path.exists(asset_manifest_path):
        return FileResponse(asset_manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

# Catch-all route (LAST)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    """Diagnostic catch-all route"""
    print(f"🔍 Catch-all hit: {full_path}")

    # If an API route reaches here, log it as an error
    if any(full_path.startswith(prefix) for prefix in ["api/", "ws/"]):
        print(f"❌ ERROR: API route reached catch-all: {full_path}")
        print(f"   This means the API routers are not working correctly!")

        # Return detailed error for diagnostics
        return JSONResponse(
            status_code=500,
            content={
                "error": "API routing error",
                "message": f"API route {full_path} reached catch-all handler",
                "path": full_path,
                "method": request.method,
                "headers": dict(request.headers),
                "debug": "Check container logs for import/registration errors"
            }
        )

    # Handle static files (simplified)
    if any(full_path.endswith(ext) for ext in ['.js', '.css', '.map', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.json']):
        print(f"🔍 Static asset requested: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

    # Serve React index.html
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
    print("🎯 Starting diagnostic server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)