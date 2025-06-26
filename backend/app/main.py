# backend/app/main.py - CORRECT PREFIX VERSION
"""
FastAPI main application with proper reverse proxy prefix handling
Based on user's working solution
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
    title="PowerBI Agent API - CORRECT PREFIX",
    description="Proper reverse proxy prefix handling",
    version="1.0.0-prefix-fix"
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

# Register API routes with proper prefix
print("📡 Registering API routes...")

if reverse_proxy:
    # For reverse proxy: mount with /talk4finance prefix
    print("🔄 Using reverse proxy mode - mounting with /talk4finance prefix")
    app.include_router(auth_router, prefix="/talk4finance/api/auth", tags=["auth"])
else:
    # For direct access: mount without prefix
    print("🔗 Using direct mode - mounting without prefix")
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

print("✅ Auth router registered successfully")

# Print all auth routes for verification
for route in auth_router.routes:
    methods = getattr(route, 'methods', ['UNKNOWN'])
    path = getattr(route, 'path', 'UNKNOWN')
    print(f"   📝 Auth route: {methods} {path}")

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting up prefix-corrected API...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

# Essential routes with proper prefix
if reverse_proxy:
    @app.get("/talk4finance/health")
    async def health_check():
        print("💚 Health check called (reverse proxy)")
        return {
            "status": "healthy",
            "service": "Talk4Finance API - PREFIX FIX",
            "mode": "reverse_proxy"
        }

    @app.get("/talk4finance/api")
    async def api_info():
        print("📋 API info called (reverse proxy)")
        return {
            "message": "PowerBI Agent API - PREFIX FIX",
            "version": "1.0.0-prefix-fix",
            "mode": "reverse_proxy"
        }

    @app.get("/talk4finance/debug/routes")
    async def debug_routes():
        """Debug endpoint to see all registered routes"""
        print("🔍 Debug routes endpoint called (reverse proxy)")
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        return {"routes": routes, "total": len(routes)}
else:
    @app.get("/health")
    async def health_check():
        print("💚 Health check called (direct)")
        return {
            "status": "healthy",
            "service": "Talk4Finance API - PREFIX FIX",
            "mode": "direct"
        }

    @app.get("/api")
    async def api_info():
        print("📋 API info called (direct)")
        return {
            "message": "PowerBI Agent API - PREFIX FIX",
            "version": "1.0.0-prefix-fix",
            "mode": "direct"
        }

    @app.get("/debug/routes")
    async def debug_routes():
        """Debug endpoint to see all registered routes"""
        print("🔍 Debug routes endpoint called (direct)")
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        return {"routes": routes, "total": len(routes)}

# CORS preflight handler with proper prefix
if reverse_proxy:
    @app.options("/talk4finance/{rest_of_path:path}")
    async def preflight_handler(rest_of_path: str):
        print(f"🔄 CORS preflight for: /talk4finance/{rest_of_path}")
        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "*",
        })
else:
    @app.options("/{rest_of_path:path}")
    async def preflight_handler(rest_of_path: str):
        print(f"🔄 CORS preflight for: {rest_of_path}")
        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "*",
        })

# Static file mounting with proper prefix
print("📁 Setting up static file serving...")

static_dir = "/app/static"

if os.path.exists(static_dir):
    print(f"📁 Static directory found: {static_dir}")

    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        if reverse_proxy:
            print(f"✅ Mounting React static files at /talk4finance/static from: {react_static_dir}")
            app.mount("/talk4finance/static", StaticFiles(directory=react_static_dir), name="react_static")
        else:
            print(f"✅ Mounting React static files at /static from: {react_static_dir}")
            app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
    else:
        print(f"❌ React static subdirectory not found")
        if reverse_proxy:
            app.mount("/talk4finance/static", StaticFiles(directory=static_dir), name="main_static")
        else:
            app.mount("/static", StaticFiles(directory=static_dir), name="main_static")

    # Also mount assets directory
    if reverse_proxy:
        app.mount("/talk4finance/assets", StaticFiles(directory=static_dir), name="assets_static")
    else:
        app.mount("/assets", StaticFiles(directory=static_dir), name="assets_static")

    print(f"✅ Static file mounting complete")
else:
    print(f"❌ Static directory not found: {static_dir}")

# Common file routes with proper prefix
if reverse_proxy:
    @app.get("/talk4finance/asset-manifest.json")
    async def asset_manifest():
        asset_manifest_path = "/app/static/asset-manifest.json"
        print(f"🔍 Asset manifest requested (reverse proxy): {asset_manifest_path}")
        if os.path.exists(asset_manifest_path):
            return FileResponse(asset_manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

    @app.get("/talk4finance/favicon.ico")
    async def favicon():
        favicon_path = "/app/static/favicon.ico"
        print(f"🔍 Favicon requested (reverse proxy): {favicon_path}")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.get("/talk4finance/manifest.json")
    async def manifest():
        manifest_path = "/app/static/manifest.json"
        print(f"🔍 Manifest requested (reverse proxy): {manifest_path}")
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Manifest not found"})
else:
    @app.get("/asset-manifest.json")
    async def asset_manifest():
        asset_manifest_path = "/app/static/asset-manifest.json"
        print(f"🔍 Asset manifest requested (direct): {asset_manifest_path}")
        if os.path.exists(asset_manifest_path):
            return FileResponse(asset_manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Asset manifest not found"})

    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = "/app/static/favicon.ico"
        print(f"🔍 Favicon requested (direct): {favicon_path}")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return JSONResponse(status_code=404, content={"detail": "Favicon not found"})

    @app.get("/manifest.json")
    async def manifest():
        manifest_path = "/app/static/manifest.json"
        print(f"🔍 Manifest requested (direct): {manifest_path}")
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Manifest not found"})

# Catch-all route with proper prefix - MUST be absolutely last
if reverse_proxy:
    @app.get("/talk4finance/{full_path:path}")
    async def serve_react_app(full_path: str, request: Request):
        """Catch-all for reverse proxy with /talk4finance prefix"""
        print(f"🔍 Catch-all hit (reverse proxy): /talk4finance/{full_path}")

        # Handle static files as you suggested
        if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
            print(f"!!! NOT HTML FILE: {full_path}")
            asset_path = f"/app/static/{full_path}"
            if os.path.exists(asset_path):
                print(f"✅ Found asset at: {asset_path}")
                return FileResponse(asset_path)
            else:
                print(f"❌ Asset not found: {asset_path}")
                return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

        # Serve React index.html for everything else
        index_path = "/app/static/index.html"
        if os.path.exists(index_path):
            print(f"✅ Serving React index.html for: {full_path}")
            return FileResponse(index_path, media_type="text/html")
        else:
            print(f"❌ React index.html not found")
            return JSONResponse(status_code=404, content={"detail": "React app not found"})
else:
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str, request: Request):
        """Catch-all for direct access without prefix"""
        print(f"🔍 Catch-all hit (direct): {full_path}")

        # Handle static files
        if any(full_path.endswith(suffix) for suffix in [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json"]):
            print(f"!!! NOT HTML FILE: {full_path}")
            asset_path = f"/app/static/{full_path}"
            if os.path.exists(asset_path):
                print(f"✅ Found asset at: {asset_path}")
                return FileResponse(asset_path)
            else:
                print(f"❌ Asset not found: {asset_path}")
                return JSONResponse(status_code=404, content={"detail": f"Asset not found: {full_path}"})

        # Serve React index.html for everything else
        index_path = "/app/static/index.html"
        if os.path.exists(index_path):
            print(f"✅ Serving React index.html for: {full_path}")
            return FileResponse(index_path, media_type="text/html")
        else:
            print(f"❌ React index.html not found")
            return JSONResponse(status_code=404, content={"detail": "React app not found"})

print("🎯 Prefix-corrected server setup complete!")

if __name__ == "__main__":
    print("🎯 Starting prefix-corrected server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)