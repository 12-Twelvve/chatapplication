"""
FastAPI application initialization and configuration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables
from app.routers import user, auth, chat
import os

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    """Create database tables on application startup."""
    create_db_and_tables()


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
async def read_root():
    """
    Serves the index.html file from the static directory at the root URL.
    """
    index_html_path = os.path.join("static", "index.html")
    
    # Check if the file exists to avoid a server error
    if not os.path.exists(index_html_path):
        raise HTTPException(status_code=404, detail="index.html not found")
        
    return FileResponse(index_html_path, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)