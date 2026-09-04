from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.audit import router as audit_router
from app.api.payments import router as payments_router
from app.api.recovery import router as recovery_router
from app.api.simulation import router as simulation_router


app = FastAPI(
    title="REVIVE AI",
    description="AI-powered revenue recovery controller",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
