# backend/app/main.py - SIMPLIFIED WORKING VERSION

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response, Request
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

# Detect if we're behind a reverse proxy
def is_reverse_proxy_env():
    """Check if we're running behind a reverse proxy (DocaCloud)"""
    return os.getenv('HTTP_X_FORWARDED_PREFIX') == '/talk4finance' or \
        os.getenv('REVERSE_PROXY') == 'true'

# Initialize FastAPI app
root_path = "/talk4finance" if is_reverse_proxy_env() else None

app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0",
    root_path=root_path
)

print(f"🚀 Starting FastAPI with root_path: {root_path}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Simple middleware to handle double slashes
@app.middleware("http")
async def fix_paths(request: Request, call_next):
    path = request.url.path
    if path.startswith('//'):
        fixed_path = path[1:]
        print(f"🔧 Fixed path: {path} -> {fixed_path}")
        scope = request.scope.copy()
        scope["path"] = fixed_path
        scope["raw_path"] = fixed_path.encode()
        request = Request(scope, request.receive)

    response = await call_next(request)
    return response

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

# Mount API routes FIRST
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

# WebSocket endpoint
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

                    await manager.send_personal_message(
                        json.dumps({"type": "message", "response": response, "typing": False}),
                        user_id
                    )

                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({"type": "error", "error": f"Error: {str(e)}", "typing": False}),
                        user_id
                    )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount static files - React build structure
static_dir = "/app/static"
if os.path.exists(static_dir):
    # React creates nested static folder: /app/static/static/
    react_static_path = os.path.join(static_dir, "static")
    if os.path.exists(react_static_path):
        # Mount the nested static directory to handle /static/ routes
        app.mount("/static", StaticFiles(directory=react_static_path), name="static")
        print(f"✅ Mounted static files from: {react_static_path}")

# Handle specific files
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("/app/static/favicon.ico") if os.path.exists("/app/static/favicon.ico") else JSONResponse(status_code=404, content={})

@app.get("/asset-manifest.json")
async def asset_manifest():
    return FileResponse("/app/static/asset-manifest.json") if os.path.exists("/app/static/asset-manifest.json") else JSONResponse(status_code=404, content={})

# Catch-all for React routing - MUST BE LAST
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Don't serve index.html for API routes or missing static files
    if full_path.startswith('api/'):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # Serve index.html for all React routes
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return JSONResponse(status_code=404, content={"detail": "App not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)