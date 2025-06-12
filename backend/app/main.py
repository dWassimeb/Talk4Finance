# backend/app/main.py - CLEAN VERSION
"""
FastAPI main application for PowerBI Agent
Serves React frontend and provides API endpoints
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
from app.chat.services import ChatService

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
        "http://localhost:3000",           # Local development
        "http://localhost:8000",           # Local backend testing
        "http://castor.iagen-ov.fr",       # Production domain
        "http://castor.iagen-ov.fr/talk4finance",  # Production with subpath
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

# API endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API"}

@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API", "version": "1.0.0"}

# Static files setup
static_dir = "/app/static"  # Docker path
# static_dir = "/Users/wassime/Desktop/Talk4Finance/frontend/build"  # Local testing

if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    # Check for React's nested static directory structure
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        print(f"✅ Mounting React static files from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="static")
    else:
        print(f"⚠️  No nested static dir, mounting main directory: {static_dir}")
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"❌ Static directory not found: {static_dir}")

# Catch-all route for React Router (MUST BE LAST)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all non-API routes"""

    # Don't serve React for API routes or static files
    if any(full_path.startswith(prefix) for prefix in ["api/", "ws/", "health", "docs", "static/"]):
        return JSONResponse(status_code=404, content={"detail": f"Not found: {full_path}"})

    # Serve React index.html for all other routes
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "React build not found", "path": index_path}
        )

if __name__ == "__main__":
    print("🚀 Starting Talk4Finance API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")