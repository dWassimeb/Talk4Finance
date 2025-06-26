# backend/app/main.py - HYBRID VERSION
"""
FastAPI main application with BOTH prefixed and non-prefixed routes
Handles both reverse proxy and direct access
"""
from fastapi import FastAPI, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

print("🔍 Testing core imports...")
try:
    from app.database.connection import init_db
    print("✅ Database import OK")
except Exception as e:
    print(f"❌ Database import failed: {e}")

try:
    from app.auth.routes import auth_router
    print("✅ Auth router import OK")
    print(f"   Auth router has {len(auth_router.routes)} routes")
except Exception as e:
    print(f"❌ Auth router import failed: {e}")

# Detect if we're behind a reverse proxy
def is_reverse_proxy_env():
    """Check if we're running behind a reverse proxy (DocaCloud)"""
    return os.getenv('HTTP_X_FORWARDED_PREFIX') == '/talk4finance' or \
        os.getenv('REVERSE_PROXY') == 'true'

reverse_proxy = is_reverse_proxy_env()
print(f"🔍 Reverse proxy mode: {reverse_proxy}")

# Initialize FastAPI app
app = FastAPI(
    title="PowerBI Agent API - HYBRID",
    description="Handles both prefixed and non-prefixed routes",
    version="1.0.0-hybrid"
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

# Register API routes - BOTH with and without prefix
print("📡 Registering API routes...")

# Always include non-prefixed routes (for health checks, direct access)
app.include_router(auth_router, prefix="/api/auth", tags=["auth-direct"])
print("✅ Non-prefixed auth router registered")

# If reverse proxy, ALSO include prefixed routes
if reverse_proxy:
    app.include_router(auth_router, prefix="/talk4finance/api/auth", tags=["auth-proxy"])
    print("✅ Prefixed auth router registered for reverse proxy")

# Print all auth routes for verification
for route in auth_router.routes:
    methods = getattr(route, 'methods', ['UNKNOWN'])
    path = getattr(route, 'path', 'UNKNOWN')
    print(f"   📝 Auth route: {methods} {path}")

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up hybrid API...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

# Essential routes - BOTH versions
@app.get("/health")
async def health_check():
    print("💚 Health check called (non-prefixed)")
    return {
        "status": "healthy",
        "service": "Talk4Finance API - HYBRID",
        "mode": "non-prefixed"
    }

@app.get("/api")
async def api_info():
    print("📋 API info called (non-prefixed)")
    return {
        "message": "PowerBI Agent API - HYBRID",
        "version": "1.0.0-hybrid",
        "mode": "non-prefixed"
    }

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to see all registered routes"""
    print("🔍 Debug routes endpoint called (non-prefixed)")
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unnamed')
            })
    return {"routes": routes, "total": len(routes)}

# If reverse proxy, also add prefixed versions
if reverse_proxy:
    @app.get("/talk4finance/health")
    async def health_check_prefixed():
        print("💚 Health check called (prefixed)")
        return {
            "status": "healthy",
            "service": "Talk4Finance API - HYBRID",
            "mode": "prefixed"
        }

    @app.get("/talk4finance/api")
    async def api_info_prefixed():
        print("📋 API info called (prefixed)")
        return {
            "message": "PowerBI Agent API - HYBRID",
            "version": "1.0.0-hybrid",
            "mode": "prefixed"
        }

    @app.get("/talk4finance/debug/routes")
    async def debug_routes_prefixed():
        """Debug endpoint to see all registered routes"""
        print("🔍 Debug routes endpoint called (prefixed)")
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        return {"routes": routes, "total": len(routes)}

# CORS preflight handlers - BOTH versions
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    print(f"🔄 CORS preflight for: {rest_of_path}")
    return Response(status_code=204, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

if reverse_proxy:
    @app.options("/talk4finance/{rest_of_path:path}")
    async def preflight_handler_prefixed(rest_of_path: str):
        print(f"🔄 CORS preflight for: /talk4finance/{rest_of_path}")
        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "*",
        })

# Static file mounting - BOTH versions
print("📁 Setting up static file serving...")

static_dir = "/app/static"

if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        # Non-prefixed static files
        print(f"✅ Mounting React static files at /static from: {react_static_dir}")
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")

        # Prefixed static files for reverse proxy
        if reverse_proxy:
            print(f"✅ Mounting React static files at /talk4finance/static from: {react_static_dir}")
            app.mount("/talk4finance/static", StaticFiles(directory=react_static_dir), name="react_static_prefixed")
    else:
        print(f"❌ React static subdirectory not found")
        app.mount("/static", StaticFiles(directory=static_dir), name="main_static")
        if reverse_proxy:
            app.mount("/talk4finance/static", StaticFiles(directory=static_dir), name="main_static_prefixed")

    # Also mount assets directory - BOTH versions
    app.mount("/assets", StaticFiles(directory=static_dir), name="assets_static")
    if reverse_proxy:
        app.mount("/talk4finance/assets", StaticFiles(directory=static_dir), name="assets_static_prefixed")

    print(f"✅ Static file mounting complete")
else:
    print(f"❌ Static directory not found: {static_dir}")

# Common file routes - BOTH versions
@app.get("/asset-manifest.json")
async def asset_manifest():
    asset_manifest_path = "/app/static/asset-manifest.json"
    print(f"🔍 Asset manifest requested (non-prefixed): {asset_manifest_path}")
    if os.path.exists(asset_manifest_path):
        return FileResponse(asset_manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

@app.get("/favicon.ico")
async def favicon():
    favicon_path = "/app/static/favicon.ico"
    print(f"🔍 Favicon requested (non-prefixed): {favicon_path}")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

@app.get("/manifest.json")
async def manifest():
    manifest_path = "/app/static/manifest.json"
    print(f"🔍 Manifest requested (non-prefixed): {manifest_path}")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

# Prefixed versions
if reverse_proxy:
    @app.get("/talk4finance/asset-manifest.json")
    async def asset_manifest_prefixed():
        asset_manifest_path = "/app/static/asset-manifest.json"
        print(f"🔍 Asset manifest requested (prefixed): {asset_manifest_path}")
        if os.path.exists(asset_manifest_path):
            return FileResponse(asset_manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

    @app.get("/talk4finance/favicon.ico")
    async def favicon_prefixed():
        favicon_path = "/app/static/favicon.ico"
        print(f"🔍 Favicon requested (prefixed): {favicon_path}")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.get("/talk4finance/manifest.json")
    async def manifest_prefixed():
        manifest_path = "/app/static/manifest.json"
        print(f"🔍 Manifest requested (prefixed): {manifest_path}")
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

# Catch-all routes - BOTH versions, but prefixed one has priority
if reverse_proxy:
    @app.get("/talk4finance/{full_path:path}")
    async def serve_react_app_prefixed(full_path: str, request: Request):
        """Catch-all for reverse proxy with /talk4finance prefix"""
        print(f"🔍 Catch-all hit (prefixed): /talk4finance/{full_path}")

        # Handle static files
        if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
            print(f"!!! NOT HTML FILE: {full_path}")
            # Try nested static directory first
            asset_path = f"/app/static/static/{full_path}"
            if os.path.exists(asset_path):
                print(f"✅ Found asset at: {asset_path}")
                return FileResponse(asset_path)
            # Fallback to main static directory
            asset_path = f"/app/static/{full_path}"
            if os.path.exists(asset_path):
                print(f"✅ Found asset at: {asset_path}")
                return FileResponse(asset_path)
            else:
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

# Add this BEFORE the catch-all routes in main.py

# Handle double slash routes (reverse proxy issue)
if reverse_proxy:
    # Register auth routes with double slashes for reverse proxy
    from fastapi import APIRouter

    # Create a duplicate router for double slash paths
    double_slash_auth_router = APIRouter()

    # Import the actual route functions and re-register them
    from app.auth.routes import register, login, get_current_user_info

    # Re-register with double slash paths
    double_slash_auth_router.add_api_route("//api/auth/register", register, methods=["POST"])
    double_slash_auth_router.add_api_route("//api/auth/login", login, methods=["POST"])
    double_slash_auth_router.add_api_route("//api/auth/me", get_current_user_info, methods=["GET"])

    app.include_router(double_slash_auth_router, tags=["auth-double-slash"])
    print("✅ Double slash auth routes registered")

    # Also register prefixed double slash routes
    double_slash_prefixed_auth_router = APIRouter()
    double_slash_prefixed_auth_router.add_api_route("//talk4finance/api/auth/register", register, methods=["POST"])
    double_slash_prefixed_auth_router.add_api_route("//talk4finance/api/auth/login", login, methods=["POST"])
    double_slash_prefixed_auth_router.add_api_route("//talk4finance/api/auth/me", get_current_user_info, methods=["GET"])

    app.include_router(double_slash_prefixed_auth_router, tags=["auth-prefixed-double-slash"])
    print("✅ Double slash prefixed auth routes registered")

# Non-prefixed catch-all (lower priority)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    """Catch-all for direct access without prefix"""
    print(f"🔍 Catch-all hit (non-prefixed): {full_path}")

    # Skip if this looks like it should be handled by prefixed route
    if reverse_proxy and full_path.startswith('talk4finance/'):
        print(f"⏭️ Skipping - should be handled by prefixed route")
        return JSONResponse(status_code=404, content={"detail": "Use prefixed route"})

    # Handle static files
    if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
        print(f"!!! NOT HTML FILE: {full_path}")
        # Try nested static directory first
        asset_path = f"/app/static/static/{full_path}"
        if os.path.exists(asset_path):
            print(f"✅ Found asset at: {asset_path}")
            return FileResponse(asset_path)
        # Fallback to main static directory
        asset_path = f"/app/static/{full_path}"
        if os.path.exists(asset_path):
            print(f"✅ Found asset at: {asset_path}")
            return FileResponse(asset_path)
        else:
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

print("🎯 Hybrid server setup complete!")

if __name__ == "__main__":
    print("🎯 Starting hybrid server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)