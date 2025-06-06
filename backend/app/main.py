# backend/app/main.py
"""
FastAPI main application for PowerBI Agent
Updated to serve React frontend in production
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
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

# CORS middleware - Updated for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local development
        "http://frontend:3000",            # Docker frontend
        "http://31.44.217.0",              # Your production domain
        "https://31.44.217.0",             # HTTPS version
        "http://localhost:8000",           # Local backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
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
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process the message
            question = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id")

            if question:
                # Send typing indicator
                await manager.send_message(user_id, {
                    "type": "typing",
                    "typing": True
                })

                try:
                    # Get response from PowerBI agent
                    response = await chat_service.process_message(
                        user_id=user_id,
                        message=question,
                        conversation_id=conversation_id
                    )

                    # Send response back to client
                    await manager.send_message(user_id, {
                        "type": "message",
                        "response": response,
                        "typing": False
                    })

                except Exception as e:
                    # Send error message
                    await manager.send_message(user_id, {
                        "type": "error",
                        "error": f"Error processing your question: {str(e)}",
                        "typing": False
                    })

    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API info endpoint
@app.get("/api")
async def api_info():
    return {"message": "PowerBI Agent API is running", "version": "1.0.0"}

# Serve static files (CSS, JS, images) from React build
static_dir = "/app/static"
if os.path.exists(static_dir):
    # Check if there's a nested static folder (common in React builds)
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        app.mount("/static", StaticFiles(directory=react_static_dir), name="static")

    # Also serve other assets directly from the main static directory
    app.mount("/assets", StaticFiles(directory=static_dir), name="assets")

# Serve favicon
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

# IMPORTANT: This catch-all route must be LAST
# Serve React app for all other routes
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve React app for all routes that don't match API endpoints.
    This enables React Router to handle client-side routing.
    """
    # Skip API routes, docs, WebSocket
    if any(full_path.startswith(prefix) for prefix in [
        "api/", "ws/", "health", "docs", "openapi.json", "redoc", "static/", "assets/"
    ]):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # Serve React index.html for all other routes
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "React build not found",
                "static_exists": os.path.exists("/app/static"),
                "static_contents": os.listdir("/app/static") if os.path.exists("/app/static") else []
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )