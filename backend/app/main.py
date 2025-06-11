# backend/app/main.py - FIXED FOR SUBPATH DEPLOYMENT
"""
FastAPI main application for PowerBI Agent
Updated for subpath deployment behind reverse proxy
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
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

# Initialize FastAPI app with subpath support
app = FastAPI(
    title="PowerBI Agent API",
    description="Natural language interface to PowerBI datasets",
    version="1.0.0",
    root_path="/talk4finance"  # This is crucial for subpath deployment
)

# CORS middleware for subpath deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local development frontend
        "http://localhost:3001",           # Docker mapped port
        "http://127.0.0.1:3000",          # Alternative localhost
        "http://127.0.0.1:3001",          # Alternative localhost with mapped port
        "http://31.44.217.0",             # Production domain root
        "http://31.44.217.0/talk4finance", # Production domain with subpath
        "http://castor.iagen-ov.fr",      # Production domain root
        "http://castor.iagen-ov.fr/talk4finance", # Production domain with subpath
        "https://castor.iagen-ov.fr",     # HTTPS version
        "https://castor.iagen-ov.fr/talk4finance", # HTTPS version with subpath
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
    print("Starting up Talk4Finance API...")
    await init_db()
    print("Database initialized successfully")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Talk4Finance API", "subpath": "/talk4finance"}

# API info endpoint
@app.get("/api")
async def api_info():
    return {
        "message": "PowerBI Agent API is running",
        "version": "1.0.0",
        "subpath": "/talk4finance",
        "endpoints": {
            "auth": "/talk4finance/api/auth",
            "chat": "/talk4finance/api/chat",
            "health": "/talk4finance/health",
            "docs": "/talk4finance/docs"
        }
    }

# CORS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Mount static files with subpath support
static_dir = "/app/static"
if os.path.exists(static_dir):
    print(f"Static directory found: {static_dir}")

    # Mount React static files at /static (they'll be accessible at /talk4finance/static)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"Mounted static files from: {static_dir}")

    # Also check for nested static folder
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        # This will handle /static/js, /static/css etc.
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
        print(f"Mounted React static files from: {react_static_dir}")
else:
    print(f"Warning: Static directory not found: {static_dir}")

# Serve favicon
@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

# Serve React app for root and other routes
@app.get("/")
async def serve_react_root():
    """Serve React app for root path"""
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "React build not found", "path": index_path}
        )

# IMPORTANT: This catch-all route must be LAST
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve React app for all routes that don't match API endpoints.
    This enables React Router to handle client-side routing.
    """
    # Skip API routes, docs, WebSocket, static files
    if any(full_path.startswith(prefix) for prefix in [
        "api/", "ws/", "health", "docs", "openapi.json", "redoc", "static/"
    ]):
        return JSONResponse(status_code=404, content={"detail": f"Not found: {full_path}"})

    # Serve React index.html for all other routes
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        print(f"Warning: React build not found at {index_path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "React build not found",
                "static_exists": os.path.exists("/app/static"),
                "static_contents": os.listdir("/app/static") if os.path.exists("/app/static") else [],
                "requested_path": full_path
            }
        )

if __name__ == "__main__":
    print("Starting Talk4Finance API server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False, # Reload disabled for production
        log_level="info"
    )