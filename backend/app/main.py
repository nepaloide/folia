import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
    )

    # ── CORS ──────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health check ─────────────────────────────────────────────────
    @app.get("/health")
    async def health():
        return {"status": "ok", "app": settings.APP_NAME}

    # ── Routers ──────────────────────────────────────────────────────
    app.include_router(v1_router, prefix="/api/v1")

    # ── Dev-mode table creation ──────────────────────────────────────
    if os.getenv("ENVIRONMENT", "").lower() in ("dev", "development", ""):
        @app.on_event("startup")
        async def create_tables():
            from app.core.database import Base, engine
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    return app


app = create_app()
