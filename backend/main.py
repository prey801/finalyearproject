import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.api import analyze, history, auth
from backend.database.session import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database tables on startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database tables: {e}. Please ensure the database is running.")
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the MedScope AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
