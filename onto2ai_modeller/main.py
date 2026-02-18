"""
Onto2AI Modeller - FastAPI Backend

A web application for reviewing and enhancing ontology schemas in stagingdb.
"""
import sys
import os

# Add parent directory to path so we can import from neo4j_onto2ai_toolset
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import router as schemas_router

app = FastAPI(
    title="Onto2AI Modeller",
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

# Static files path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates for injecting server-side config
templates = Jinja2Templates(directory=STATIC_DIR)

import argparse
import uvicorn

# Include API routers
app.include_router(schemas_router, prefix="/api")


@app.get("/")
async def root(request: Request):
    """Serve the main application page with injected config."""
    theme = os.getenv("APP_THEME", "dark")
    return templates.TemplateResponse("index.html", {"request": request, "default_theme": theme})


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "app": "Onto2AI Modeller"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Onto2AI Modeller")
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="LLM model to use (gemini, gpt, or full model name)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8180,
        help="Port to bind to"
    )
    parser.add_argument(
        "--theme", "-t",
        type=str,
        choices=["dark", "light"],
        default="dark",
        help="Default theme to start with (dark or light)"
    )
    
    args = parser.parse_args()
    
    # Store theme in environment for the root handler
    os.environ["APP_THEME"] = args.theme
    
    # Handle shorthand model names
    if args.model:
        model_name = args.model
        if model_name.lower() == "gemini":
            model_name = "gemini-3-flash-preview-001"
        elif model_name.lower() == "gemini3":
            model_name = "gemini-3-flash-preview-001"
        elif model_name.lower() == "gpt":
            model_name = "gpt-5.2"
            
        print(f"🚀 Starting Modeller with model: {model_name}")
        os.environ["LLM_MODEL_NAME"] = model_name
    else:
        print(f"🚀 Starting Modeller with default model")

    uvicorn.run(app, host=args.host, port=args.port)
