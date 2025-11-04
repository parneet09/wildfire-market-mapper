from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routes import orgs, contacts, review, export
from app.ui import admin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Wildfire Risk Tool Market Mapper",
    description="AI-powered system for mapping wildfire risk tool market opportunities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(orgs.router, prefix="/api/orgs", tags=["organizations"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

# Include UI routes
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "wildfire-market-mapper"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Wildfire Risk Tool Market Mapper API",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin"
    }

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
