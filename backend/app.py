import os
import sys
import logging

# Add parent directory of backend folder to sys.path to support direct execution
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from backend.routes import router as api_router

app = FastAPI(
    title="JobPulse API",
    description="Backend API for JobPulse to fetch posting trends, news, and run AI market assessment.",
    version="1.0.0"
)

# Configure CORS to allow communication from the React frontend
origins = [
    "http://localhost:5173",       # Default Vite dev server port
    "http://127.0.0.1:5173",
    "http://localhost:3000",       # Alternative port
    "*"                            # Fallback wildcard
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)

@app.get("/", summary="Root Health Check")
def health_check():
    return {
        "status": "healthy",
        "app": "JobPulse",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    # If run directly, launch the application
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
