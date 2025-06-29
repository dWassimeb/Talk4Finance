# backend/app/main.py - REAL POWERBI VERSION
"""
FastAPI main application with real PowerBI ChatService integration
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from typing import Dict

from app.auth.routes import auth_router
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
        "http://castor.iagen-ov.fr",
        "http://castor.iagen-ov.fr/talk4finance",
        "https://castor.iagen-ov.fr",
        "https://castor.iagen-ov.fr/talk4finance",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reverse_proxy = is_reverse_proxy_env()

# Register auth routes (multiple paths for reverse proxy compatibility)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
if reverse_proxy:
    app.include_router(auth_router, prefix="/talk4finance/api/auth", tags=["auth-proxy"])

    # Handle double slash routes
    from fastapi import APIRouter
    from app.auth.routes import register, login, get_current_user_info

    double_slash_router = APIRouter()
    double_slash_router.add_api_route("//api/auth/register", register, methods=["POST"])
    double_slash_router.add_api_route("//api/auth/login", login, methods=["POST"])
    double_slash_router.add_api_route("//api/auth/me", get_current_user_info, methods=["GET"])
    app.include_router(double_slash_router, tags=["auth-double-slash"])

# Register chat routes
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
if reverse_proxy:
    app.include_router(chat_router, prefix="/talk4finance/api/chat", tags=["chat-proxy"])

    # Handle double slash chat routes (like we did for auth)
    # Import the actual chat route functions
    from app.chat.routes import get_conversations, create_conversation, get_conversation, delete_conversation

    chat_double_slash_router = APIRouter()
    chat_double_slash_router.add_api_route("//api/chat/conversations", get_conversations, methods=["GET"])
    chat_double_slash_router.add_api_route("//api/chat/conversations", create_conversation, methods=["POST"])
    chat_double_slash_router.add_api_route("//api/chat/conversations/{conversation_id}", get_conversation, methods=["GET"])
    chat_double_slash_router.add_api_route("//api/chat/conversations/{conversation_id}", delete_conversation, methods=["DELETE"])
    app.include_router(chat_double_slash_router, tags=["chat-double-slash"])
    print("✅ Double slash chat routes registered")

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
        await manager.send_personal_message(json.dumps({
            "type": "connection",
            "message": "Connected to PowerBI Agent" if chat_service else "Connected (Echo mode)"
        }), user_id)

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            question = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id")

            print(f"📥 Received message from user {user_id}: {question}")

            if question:
                # Send typing indicator
                await manager.send_personal_message(json.dumps({
                    "type": "typing",
                    "typing": True
                }), user_id)

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
                                    "is_user": True,  # ✅ CRITICAL: Mark as user message
                                    "type": "user",
                                    "created_at": response["user_message"]["created_at"]
                                },
                                "agent_message": {
                                    "id": response["agent_message"]["id"],
                                    "content": response["agent_message"]["content"],
                                    "is_user": False,  # ✅ CRITICAL: Mark as agent message
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
                                    "is_user": True,  # ✅ CRITICAL: Mark as user message
                                    "type": "user",
                                    "created_at": "2025-01-01T00:00:00Z"
                                },
                                "agent_message": {
                                    "content": f"Echo: {question}",
                                    "is_user": False,  # ✅ CRITICAL: Mark as agent message
                                    "type": "agent",
                                    "created_at": "2025-01-01T00:00:00Z"
                                },
                                "conversation_id": conversation_id
                            }
                        }

                    await manager.send_personal_message(json.dumps(websocket_response), user_id)

                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    error_response = {
                        "type": "message",
                        "response": {
                            "user_message": {
                                "content": question,
                                "is_user": True,  # ✅ CRITICAL: Mark as user message
                                "type": "user",
                                "created_at": "2025-01-01T00:00:00Z"
                            },
                            "agent_message": {
                                "content": f"I'm sorry, I encountered an error: {str(e)}",
                                "is_user": False,  # ✅ CRITICAL: Mark as agent message
                                "type": "agent",
                                "created_at": "2025-01-01T00:00:00Z"
                            },
                            "conversation_id": conversation_id
                        }
                    }
                    await manager.send_personal_message(json.dumps(error_response), user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"🔌 User {user_id} disconnected")

# Double slash WebSocket for reverse proxy
if reverse_proxy:
    @app.websocket("//ws/{user_id}")
    async def websocket_endpoint_double(websocket: WebSocket, user_id: str):
        # Redirect to the main WebSocket handler
        await websocket_endpoint(websocket, user_id)

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("🚀 PowerBI Agent API started")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "PowerBI Agent API",
        "chatservice_available": CHATSERVICE_AVAILABLE
    }

if reverse_proxy:
    @app.get("/talk4finance/health")
    async def health_check_proxy():
        return {
            "status": "healthy",
            "service": "PowerBI Agent API",
            "chatservice_available": CHATSERVICE_AVAILABLE
        }

# Favicon routes - BOTH regular and double slash for reverse proxy
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

    # Handle double slash favicon requests
    @app.get("//favicon.ico")
    async def favicon_double_slash():
        favicon_path = "/app/static/favicon.ico"
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.get("//talk4finance/favicon.ico")
    async def favicon_proxy_double_slash():
        favicon_path = "/app/static/favicon.ico"
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

# CORS preflight
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Manifest routes - BOTH regular and double slash for reverse proxy
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

    @app.get("//manifest.json")
    async def manifest_double_slash():
        manifest_path = "/app/static/manifest.json"
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

    @app.get("//talk4finance/manifest.json")
    async def manifest_proxy_double_slash():
        manifest_path = "/app/static/manifest.json"
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

# Static file serving
static_dir = "/app/static"

if os.path.exists(static_dir):
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
        if reverse_proxy:
            app.mount("/talk4finance/static", StaticFiles(directory=react_static_dir), name="react_static_proxy")

    app.mount("/assets", StaticFiles(directory=static_dir), name="assets")
    if reverse_proxy:
        app.mount("/talk4finance/assets", StaticFiles(directory=static_dir), name="assets_proxy")

# Asset manifest
@app.get("/asset-manifest.json")
async def asset_manifest():
    asset_manifest_path = "/app/static/asset-manifest.json"
    if os.path.exists(asset_manifest_path):
        return FileResponse(asset_manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

if reverse_proxy:
    @app.get("/talk4finance/asset-manifest.json")
    async def asset_manifest_proxy():
        asset_manifest_path = "/app/static/asset-manifest.json"
        if os.path.exists(asset_manifest_path):
            return FileResponse(asset_manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

    @app.get("//asset-manifest.json")
    async def asset_manifest_double_slash():
        asset_manifest_path = "/app/static/asset-manifest.json"
        if os.path.exists(asset_manifest_path):
            return FileResponse(asset_manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

    @app.get("//talk4finance/asset-manifest.json")
    async def asset_manifest_proxy_double_slash():
        asset_manifest_path = "/app/static/asset-manifest.json"
        if os.path.exists(asset_manifest_path):
            return FileResponse(asset_manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

# Catch-all routes for React SPA
if reverse_proxy:
    @app.get("/talk4finance/{full_path:path}")
    async def serve_react_app_proxy(full_path: str):
        if any(full_path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
            asset_path = f"/app/static/static/{full_path}"
            if os.path.exists(asset_path):
                return FileResponse(asset_path)
            asset_path = f"/app/static/{full_path}"
            if os.path.exists(asset_path):
                return FileResponse(asset_path)
            return JSONResponse(status_code=404, content={"detail": "Asset not found"})

        index_path = "/app/static/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        return JSONResponse(status_code=404, content={"detail": "React app not found"})

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    if reverse_proxy and full_path.startswith('talk4finance/'):
        return JSONResponse(status_code=404, content={"detail": "Use prefixed route"})

    if any(full_path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
        asset_path = f"/app/static/static/{full_path}"
        if os.path.exists(asset_path):
            return FileResponse(asset_path)
        asset_path = f"/app/static/{full_path}"
        if os.path.exists(asset_path):
            return FileResponse(asset_path)
        return JSONResponse(status_code=404, content={"detail": "Asset not found"})

    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "React app not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)