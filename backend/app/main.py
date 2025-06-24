# backend/app/main.py - MANUAL STATIC FILE HANDLING

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import json
import os
import mimetypes
from typing import Dict, List
import asyncio

from app.auth.routes import auth_router
from app.chat.routes import chat_router
from app.auth.dependencies import get_current_user
from app.database.connection import init_db
from app.chat.services import ChatService
from app.core.config import settings

# Initialize FastAPI app
root_path = "/talk4finance" if os.getenv('REVERSE_PROXY') == 'true' else None

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

# Middleware to handle double slashes
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

# API routes
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

# MANUAL STATIC FILE HANDLING - Handle /static/* routes explicitly
@app.get("/static/{file_path:path}")
async def serve_static_files(file_path: str):
    """Manually serve static files from React build"""
    print(f"📁 Static file requested: /static/{file_path}")

    # The React build puts files in: /app/static/static/
    static_file_path = f"/app/static/static/{file_path}"

    print(f"🔍 Looking for file at: {static_file_path}")

    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        print(f"✅ Found static file: {static_file_path}")

        # Determine the correct media type
        media_type, _ = mimetypes.guess_type(static_file_path)
        if media_type is None:
            if file_path.endswith('.js'):
                media_type = "application/javascript"
            elif file_path.endswith('.css'):
                media_type = "text/css"
            elif file_path.endswith('.json'):
                media_type = "application/json"
            else:
                media_type = "text/plain"

        return FileResponse(static_file_path, media_type=media_type)

    print(f"❌ Static file not found: {static_file_path}")

    # Debug: Show what files are actually there
    static_dir = "/app/static/static"
    if os.path.exists(static_dir):
        print(f"📋 Available files in {static_dir}:")
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), static_dir)
                print(f"   - {rel_path}")

    return JSONResponse(status_code=404, content={"detail": f"Static file not found: {file_path}"})

# Handle root-level assets
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

@app.get("/asset-manifest.json")
async def asset_manifest():
    manifest_path = "/app/static/asset-manifest.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

# CORS preflight
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Catch-all for React routing - MUST BE LAST
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    print(f"🔍 Catch-all hit: {full_path}")

    # This should NOT be reached for static files now
    if full_path.startswith('static/'):
        print(f"❌ ERROR: Static file reached catch-all! This should not happen: {full_path}")
        return JSONResponse(status_code=500, content={"error": "Static routing failed"})

    # Don't serve index.html for API routes
    if any(full_path.startswith(prefix) for prefix in ["api/", "ws/"]):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # Serve index.html for all React routes
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for: {full_path}")
        return FileResponse(index_path, media_type="text/html")

    return JSONResponse(status_code=404, content={"detail": "App not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)