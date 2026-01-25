"""
Onto2AI Model Manager - FastAPI Backend

A web application for reviewing and enhancing ontology schemas in stagingdb.
"""
import sys
import os

# Add parent directory to path so we can import from neo4j_onto2ai_toolset
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import router as schemas_router

app = FastAPI(
    title="Onto2AI Model Manager",
    description="Web application to review and enhance ontology schemas",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(schemas_router, prefix="/api")


@app.get("/")
async def root():
    """Serve the main application page."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "app": "Onto2AI Model Manager"}
