# backend/app/main.py - MINIMAL TEST VERSION
"""
Minimal test version - Remove all problematic imports to isolate the issue
"""
from fastapi import FastAPI, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Test basic imports first
try:
    print("🧪 Testing core imports...")
    from app.database.connection import init_db
    print("✅ Database import OK")
except Exception as e:
    print(f"❌ Database import failed: {e}")

try:
    from app.core.config import settings
    print("✅ Config import OK")
except Exception as e:
    print(f"❌ Config import failed: {e}")

try:
    from app.auth.dependencies import get_current_user
    print("✅ Auth dependencies import OK")
except Exception as e:
    print(f"❌ Auth dependencies import failed: {e}")

# Try importing auth router (this should work)
try:
    from app.auth.routes import auth_router
    print("✅ Auth router import OK")
    print(f"   Auth router has {len(auth_router.routes)} routes")
except Exception as e:
    print(f"❌ Auth router import failed: {e}")
    # Create dummy auth router
    from fastapi import APIRouter
    auth_router = APIRouter()

    @auth_router.post("/login")
    async def dummy_login():
        return {"error": "Auth router import failed", "details": str(e)}

    @auth_router.post("/register")
    async def dummy_register():
        return {"error": "Auth router import failed", "details": str(e)}

# Skip ChatService import for now - this is likely the problem
print("⏭️ Skipping ChatService import to test if this is the issue")

# Initialize FastAPI app
app = FastAPI(
    title="PowerBI Agent API - MINIMAL TEST",
    description="Testing API routing without ChatService",
    version="1.0.0-test"
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

# Include ONLY auth router for testing
try:
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    print("✅ Auth router registered successfully")

    # Print all auth routes for verification
    for route in auth_router.routes:
        methods = getattr(route, 'methods', ['UNKNOWN'])
        path = getattr(route, 'path', 'UNKNOWN')
        print(f"   📝 Auth route: {methods} {path}")

except Exception as e:
    print(f"❌ Auth router registration failed: {e}")

print("📡 Router registration complete!")

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up minimal test API...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

# Essential routes
@app.get("/health")
async def health_check():
    print("💚 Health check called")
    return {
        "status": "healthy",
        "service": "Talk4Finance API - MINIMAL TEST",
        "auth_router_routes": len(auth_router.routes)
    }

@app.get("/api")
async def api_info():
    print("📋 API info called")
    return {
        "message": "PowerBI Agent API - MINIMAL TEST",
        "version": "1.0.0-test",
        "auth_routes": [
            f"{getattr(route, 'methods', ['UNKNOWN'])} {getattr(route, 'path', 'UNKNOWN')}"
            for route in auth_router.routes
        ]
    }

# Test endpoint to verify auth router is working
@app.post("/test-direct-login")
async def test_direct_login():
    print("🧪 Direct test login endpoint called")
    return {"message": "Direct login endpoint working", "status": "success"}

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

# CORS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    print(f"🔄 CORS preflight for: {rest_of_path}")
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

# Static file handling (simplified for testing)
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

# Common file routes
@app.get("/asset-manifest.json")
async def asset_manifest():
    asset_manifest_path = "/app/static/asset-manifest.json"
    print(f"🔍 Asset manifest requested: {asset_manifest_path}")
    if os.path.exists(asset_manifest_path):
        return FileResponse(asset_manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

# Simple catch-all (LAST)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    """Minimal catch-all for testing"""
    print(f"🔍 Catch-all hit: {full_path}")

    # If an API route reaches here, the routers failed
    if any(full_path.startswith(prefix) for prefix in ["api/"]):
        print(f"❌ ERROR: API route reached catch-all: {full_path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "API routing error",
                "path": full_path,
                "method": request.method,
                "message": "API route reached catch-all - routers not working"
            }
        )

    # Handle static asset requests that weren't caught by mounts
    if any(full_path.endswith(ext) for ext in ['.js', '.css', '.map', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.json']):
        print(f"🔍 Static asset requested: {full_path}")

        # Clean up the path
        cleaned_path = full_path
        if cleaned_path.startswith('/'):
            cleaned_path = cleaned_path[1:]
        if cleaned_path.startswith('talk4finance/'):
            cleaned_path = cleaned_path[13:]

        print(f"🔧 Cleaned path: {cleaned_path}")

        # Try different possible paths for the asset
        possible_paths = [
            f"/app/static/{cleaned_path}",
            f"/app/static/static/{cleaned_path}",  # React puts CSS/JS in nested static
        ]

        # If it's a static/* path, try the nested structure
        if cleaned_path.startswith('static/'):
            asset_path = cleaned_path[7:]  # Remove 'static/' prefix
            possible_paths.append(f"/app/static/static/{asset_path}")

        print(f"🔍 Trying asset paths: {possible_paths}")

        for file_path in possible_paths:
            if os.path.exists(file_path):
                print(f"✅ Found asset at: {file_path}")

                # Determine correct media type
                media_type = "text/plain"
                if file_path.endswith('.js'):
                    media_type = "application/javascript"
                elif file_path.endswith('.css'):
                    media_type = "text/css"
                elif file_path.endswith('.json'):
                    media_type = "application/json"
                elif file_path.endswith('.ico'):
                    media_type = "image/x-icon"
                elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    media_type = "image/*"
                elif file_path.endswith('.svg'):
                    media_type = "image/svg+xml"

                return FileResponse(file_path, media_type=media_type)

        print(f"❌ Asset not found: {full_path}")
        return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

    # Serve React index.html for everything else
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        print(f"✅ Serving React index.html for: {full_path}")
        return FileResponse(index_path, media_type="text/html")
    else:
        print(f"❌ React index.html not found")
        return JSONResponse(status_code=404, content={"detail": "React app not found"})

if __name__ == "__main__":
    print("🎯 Starting minimal test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)