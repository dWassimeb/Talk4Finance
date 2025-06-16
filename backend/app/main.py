# backend/app/main.py - FIXED FOR DOUBLE SLASH ISSUE
"""
FastAPI main application for PowerBI Agent
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
        "https://castor.iagen-ov.fr",
        "https://castor.iagen-ov.fr/talk4finance",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers (handle both single and double slash)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth_router, prefix="//api/auth", tags=["Authentication-DoubleSlash"])
app.include_router(chat_router, prefix="//api/chat", tags=["Chat-DoubleSlash"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ WebSocket connected for user {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"❌ WebSocket disconnected for user {user_id}")

    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                print(f"📤 Message sent to user {user_id}: {message.get('type', 'unknown')}")
            except Exception as e:
                print(f"❌ Failed to send message to user {user_id}: {e}")
                self.disconnect(user_id)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f"🔌 WebSocket connection attempt for user {user_id}")
    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"📥 Received message from user {user_id}: {data}")

            try:
                message_data = json.loads(data)
                question = message_data.get("message", "")
                conversation_id = message_data.get("conversation_id")

                if question:
                    # Send typing indicator
                    await manager.send_message(user_id, {
                        "type": "typing",
                        "typing": True
                    })

                    try:
                        # Direct agent response - replace with actual PowerBI agent when ready
                        await asyncio.sleep(1)  # Brief thinking time

                        # This is where the PowerBI agent would process the query
                        # For now, just a placeholder until PowerBI integration is complete
                        response_message = "I'm ready to help with your financial analysis."

                        await manager.send_message(user_id, {
                            "type": "response",
                            "message": response_message
                        })

                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        await manager.send_message(user_id, {
                            "type": "error",
                            "message": f"I encountered an error: {str(e)}"
                        })
                    finally:
                        await manager.send_message(user_id, {
                            "type": "typing",
                            "typing": False
                        })

            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON received: {e}")
                await manager.send_message(user_id, {
                    "type": "error",
                    "message": "Invalid message format"
                })

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for user {user_id}")
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

# Handle double slash WebSocket
@app.websocket("//ws/{user_id}")
async def websocket_endpoint_double_slash(websocket: WebSocket, user_id: str):
    return await websocket_endpoint(websocket, user_id)

# Initialize database
@app.on_event("startup")
async def startup_event():
    print("🚀 Initializing database...")
    init_db()
    print("✅ Database initialized")

# Health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API"}

@app.get("//health")
async def health_check_double_slash():
    return {"status": "healthy", "service": "Talk4Finance API"}

# API info endpoints
@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

@app.get("//api")
async def api_info_double_slash():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# Mount static files
static_dir = "/app/static"
if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
        app.mount("//static", StaticFiles(directory=react_static_dir), name="react_static_double")
    else:
        print(f"❌ React static subdirectory not found")
        app.mount("/static", StaticFiles(directory=static_dir), name="main_static")
        app.mount("//static", StaticFiles(directory=static_dir), name="main_static_double")
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

@app.options("//{rest_of_path:path}")
async def preflight_handler_double_slash():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Catch-all routes for React SPA (MUST BE LAST)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all routes that don't match API endpoints or static files."""
    print(f"🔍 Single slash catch-all route hit for: {full_path}")

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

@app.get("//{full_path:path}")
async def serve_react_app_double_slash(full_path: str):
    """Handle double slash paths from nginx configuration issues."""
    print(f"🔍 Double slash catch-all route hit for: {full_path}")

    # Skip API routes, docs, websockets, and static files
    if any(full_path.startswith(prefix) for prefix in [
        "api/", "ws/", "health", "docs", "openapi.json", "redoc", "static/"
    ]):
        print(f"❌ Double slash API/Static route should not reach catch-all: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Not found: //{full_path}"})

    # Handle asset files
    if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
        print(f"🔍 Double slash asset file requested: {full_path}")
        asset_path = f"/app/static/{full_path}"
        if os.path.exists(asset_path):
            return FileResponse(asset_path)
        else:
            return JSONResponse(status_code=404, content={"detail": f"Asset not found: //{full_path}"})

    # Serve React index.html for SPA routing
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for double slash route: {full_path}")
        return FileResponse(index_path)
    else:
        print(f"❌ React index.html not found at: {index_path}")
        return JSONResponse(status_code=500, content={"error": "React build not found"})

if __name__ == "__main__":
    print("🚀 Starting Talk4Finance API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")