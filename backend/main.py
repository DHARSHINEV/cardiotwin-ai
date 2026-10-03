"""
CardioTwin AI - Backend Application Entrypoint.
Digital Twin Challenge 2026 by Happiest Health.
Tagline: "A living digital representation of the patient for earlier, personalized cardiovascular risk awareness."
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from backend.app.core.config import settings
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.models.db_models import Patient
from backend.app.api.endpoints import router as api_router
from backend.app.api.demo import router as demo_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created
    Base.metadata.create_all(bind=engine)
    
    # Check if DB has data; if empty, run initial seed
    db = SessionLocal()
    patient_count = db.query(Patient).count()
    db.close()
    
    if patient_count == 0:
        print("[CardioTwin AI] Database empty on startup. Triggering synthetic cohort generation...")
        import subprocess
        import sys
        subprocess.run([sys.executable, str(settings.DATA_DIR.parent / "scripts" / "generate_data.py"), "--quick"], check=True)

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A living digital representation of the patient for earlier, personalized cardiovascular risk awareness.",
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for frontend applications (Vite, React, Next.js, local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount both at /api and at root for full URL compatibility
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router) # Support /patients, /health, /simulation directly
app.include_router(demo_router, prefix=settings.API_V1_STR)
app.include_router(demo_router)

@app.get("/")
def root_endpoint():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "safety_disclaimer": "CardioTwin AI is a research proof-of-concept using synthetic data. It is not a medical device and does not diagnose, treat, or replace clinical judgment."
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
