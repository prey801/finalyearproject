import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from backend.api import analyze, history, auth, chat
from backend.database.session import engine, Base

HEATMAPS_DIR = os.path.join(os.environ.get("PROJECT_DIR", "/app"), "heatmaps")
os.makedirs(HEATMAPS_DIR, exist_ok=True)

UPLOADS_DIR = os.path.join(os.environ.get("PROJECT_DIR", "/app"), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist if migrations weren't run
    Base.metadata.create_all(bind=engine)
    yield

# Load allowed origins from environment (default to development origins)
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:5173"
).split(",")

app = FastAPI(
    title="MedScope AI",
    description="API for the MedScope AI automated microscopy platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Expose /metrics endpoint for Prometheus
Instrumentator().instrument(app).expose(app)

# Allow credentials only if we have specific origins
allow_credentials = "*" not in ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(chat.router)

app.mount("/heatmaps", StaticFiles(directory=HEATMAPS_DIR), name="heatmaps")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to the MedScope AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
