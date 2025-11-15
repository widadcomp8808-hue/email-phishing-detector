import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routers import analyze


def create_application() -> FastAPI:
    """
    Factory function that creates the FastAPI application instance.

    Having a dedicated factory makes it easier to configure the app in tests
    and to plug future settings (e.g. dependency injection, configuration files).
    """
    application = FastAPI(
        title="Email Phishing Detector",
        description="REST API for analyzing inbound emails and flagging phishing attempts.",
        version="0.1.0",
    )

    # Get allowed origins from environment or use defaults
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")

    # Allow the frontend to access the API
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins + ["*"],  # Allow all in production, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(analyze.router)

    # Serve static files (frontend) if the directory exists
    # Try multiple possible paths (for local dev and deployment)
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend"),
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend"),
        "/app/frontend",  # Docker path
        "./frontend",  # Relative path
    ]
    
    frontend_path = None
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, "index.html")):
            frontend_path = abs_path
            break
    
    if frontend_path:
        # Serve static files (CSS, JS)
        application.mount("/static", StaticFiles(directory=frontend_path), name="static")

        @application.get("/")
        async def serve_frontend():
            """Serve the frontend index.html"""
            index_path = os.path.join(frontend_path, "index.html")
            return FileResponse(index_path)

    return application


app = create_application()


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Lightweight endpoint to verify that the service is running.
    Useful for container orchestration readiness checks.
    """
    return {"status": "ok"}

