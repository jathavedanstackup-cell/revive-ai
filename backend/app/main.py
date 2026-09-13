from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.audit import router as audit_router
from app.api.payments import router as payments_router
from app.api.recovery import router as recovery_router
from app.api.simulation import router as simulation_router
from app.core.config import CORS_ORIGINS
from app.database.init_db import init_db
from app.database.seed import seed_demo_payments


app = FastAPI(
    title="REVIVE AI",
    description="AI-powered revenue recovery controller",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_demo_payments()


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}


app.include_router(
    payments_router,
    prefix="/api/v1",
)

app.include_router(
    recovery_router,
    prefix="/api/v1",
)

app.include_router(
    analytics_router,
    prefix="/api/v1",
)

app.include_router(
    audit_router,
    prefix="/api/v1",
)

app.include_router(
    simulation_router,
    prefix="/api/v1",
)
