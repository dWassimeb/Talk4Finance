# backend/app/main.py - COMPLETE VERSION WITH APPROVAL SYSTEM
"""
FastAPI main application with PowerBI integration and approval system
Supports 3 environments: Local, Docker, DocaCloud reverse proxy
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from typing import Dict

from app.auth.routes import auth_router  # Import the complete router
from app.chat.routes import chat_router
from app.database.connection import init_db

# Try to import ChatService, fallback to dummy if it fails
try:
    from app.chat.services import ChatService
    CHATSERVICE_AVAILABLE = True
    print("✅ ChatService imported successfully")
except Exception as e:
    print(f"❌ ChatService import failed: {e}")
    CHATSERVICE_AVAILABLE = False

# Detect reverse proxy environment
def is_reverse_proxy_env():
    return os.getenv('HTTP_X_FORWARDED_PREFIX') == '/talk4finance' or \
        os.getenv('REVERSE_PROXY') == 'true'

# Initialize FastAPI app
app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets with approval system",
    version="1.0.0"
)

print(f"🚀 Starting FastAPI")
print(f"🔍 Reverse proxy detected: {is_reverse_proxy_env()}")

# CORS middleware - comprehensive for all environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

reverse_proxy = is_reverse_proxy_env()

# Register auth routes (includes ALL approval system routes)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
if reverse_proxy:
    app.include_router(auth_router, prefix="/talk4finance/api/auth", tags=["auth-proxy"])

# Register chat routes
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
if reverse_proxy:
    app.include_router(chat_router, prefix="/talk4finance/api/chat", tags=["chat-proxy"])

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

# WebSocket endpoints with real PowerBI processing
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)

    # Initialize ChatService if available
    chat_service = None
    if CHATSERVICE_AVAILABLE:
        try:
            chat_service = ChatService()
            print(f"✅ ChatService initialized for user {user_id}")
        except Exception as e:
            print(f"❌ Failed to initialize ChatService: {e}")
            chat_service = None

    try:
        await manager.send_message(user_id, {
            "type": "connection",
            "message": "Connected to PowerBI Agent" if chat_service else "Connected (Echo mode)"
        })

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            question = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id")

            print(f"📥 Received message from user {user_id}: {question}")

            if question:
                # Send typing indicator
                await manager.send_message(user_id, {
                    "type": "typing",
                    "typing": True
                })

                try:
                    if chat_service:
                        # Use real PowerBI ChatService
                        print(f"🤖 Processing with PowerBI agent...")
                        response = await chat_service.process_message(
                            user_id=user_id,
                            message=question,
                            conversation_id=conversation_id
                        )

                        # Format response for frontend
                        websocket_response = {
                            "type": "message",
                            "response": {
                                "user_message": {
                                    "id": response["user_message"]["id"],
                                    "content": question,
                                    "is_user": True,
                                    "type": "user",
                                    "created_at": response["user_message"]["created_at"]
                                },
                                "agent_message": {
                                    "id": response["agent_message"]["id"],
                                    "content": response["agent_message"]["content"],
                                    "is_user": False,
                                    "type": "agent",
                                    "created_at": response["agent_message"]["created_at"]
                                },
                                "conversation_id": response["conversation_id"]
                            }
                        }

                    else:
                        # Fallback to echo mode
                        print(f"⚠️ Using echo mode (ChatService not available)")
                        websocket_response = {
                            "type": "message",
                            "response": {
                                "user_message": {
                                    "content": question,
                                    "is_user": True,
                                    "type": "user",
                                    "created_at": "2025-01-01T00:00:00Z"
                                },
                                "agent_message": {
                                    "content": f"Echo: {question}",
                                    "is_user": False,
                                    "type": "agent",
                                    "created_at": "2025-01-01T00:00:00Z"
                                },
                                "conversation_id": conversation_id
                            }
                        }

                    await manager.send_message(user_id, websocket_response)

                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    error_response = {
                        "type": "message",
                        "response": {
                            "user_message": {
                                "content": question,
                                "is_user": True,
                                "type": "user",
                                "created_at": "2025-01-01T00:00:00Z"
                            },
                            "agent_message": {
                                "content": f"I'm sorry, I encountered an error: {str(e)}",
                                "is_user": False,
                                "type": "agent",
                                "created_at": "2025-01-01T00:00:00Z"
                            },
                            "conversation_id": conversation_id
                        }
                    }
                    await manager.send_message(user_id, error_response)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"🔌 User {user_id} disconnected")

# Reverse proxy WebSocket support
if reverse_proxy:
    @app.websocket("/talk4finance/ws/{user_id}")
    async def websocket_endpoint_proxy(websocket: WebSocket, user_id: str):
        await websocket_endpoint(websocket, user_id)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up Talk4Finance API...")
    await init_db()
    print("✅ Database initialized successfully")

# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Talk4Finance API with Approval System",
        "chatservice_available": CHATSERVICE_AVAILABLE
    }

if reverse_proxy:
    @app.get("/talk4finance/health")
    async def health_check_proxy():
        return {
            "status": "healthy",
            "service": "Talk4Finance API with Approval System",
            "chatservice_available": CHATSERVICE_AVAILABLE
        }

# API info endpoint
@app.get("/api")
async def api_info():
    return {
        "message": "PowerBI Agent API with Approval System",
        "version": "1.0.0",
        "features": ["authentication", "approval_system", "powerbi_integration"]
    }

# CORS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Static file serving (simplified for all environments)
static_dir = "/app/static"

if os.path.exists(static_dir):
    # React's nested static files (CSS/JS)
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
        if reverse_proxy:
            app.mount("/talk4finance/static", StaticFiles(directory=react_static_dir), name="react_static_proxy")

    # General assets
    app.mount("/assets", StaticFiles(directory=static_dir), name="assets")
    if reverse_proxy:
        app.mount("/talk4finance/assets", StaticFiles(directory=static_dir), name="assets_proxy")

# Favicon handling
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

if reverse_proxy:
    @app.get("/talk4finance/favicon.ico")
    async def favicon_proxy():
        favicon_path = "/app/static/favicon.ico"
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

# Manifest handling
@app.get("/manifest.json")
async def manifest():
    manifest_path = "/app/static/manifest.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

if reverse_proxy:
    @app.get("/talk4finance/manifest.json")
    async def manifest_proxy():
        manifest_path = "/app/static/manifest.json"
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

# Catch-all for React SPA routing
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # Skip API routes
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})

    # Handle static assets
    if any(full_path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
        # Try nested static first (React build structure)
        asset_path = f"/app/static/static/{full_path}"
        if os.path.exists(asset_path):
            return FileResponse(asset_path)

        # Try root static
        asset_path = f"/app/static/{full_path}"
        if os.path.exists(asset_path):
            return FileResponse(asset_path)

        return JSONResponse(status_code=404, content={"detail": "Asset not found"})

    # Serve React index.html for all other routes (SPA routing)
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")

    return JSONResponse(status_code=404, content={"detail": "React app not found"})

# Reverse proxy catch-all
if reverse_proxy:
    @app.get("/talk4finance/{full_path:path}")
    async def serve_react_app_proxy(full_path: str):
        # Skip API routes
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})

        # Handle static assets
        if any(full_path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
            asset_path = f"/app/static/static/{full_path}"
            if os.path.exists(asset_path):
                return FileResponse(asset_path)
            asset_path = f"/app/static/{full_path}"
            if os.path.exists(asset_path):
                return FileResponse(asset_path)
            return JSONResponse(status_code=404, content={"detail": "Asset not found"})

        # Serve React index.html
        index_path = "/app/static/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        return JSONResponse(status_code=404, content={"detail": "React app not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)