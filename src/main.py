from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from database import Base, engine
import auth
import learning
import tasks
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fakarni AI Backend", version="1.0.0", description="Backend API for Fakarni learning platform")

# Setup paths
frontend_dir = Path(__file__).resolve().parent.parent / "front"

# Add middleware BEFORE static mounts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers FIRST
app.include_router(auth.router)
app.include_router(learning.router)
app.include_router(tasks.router)

# Health endpoints BEFORE static mounts
@app.get("/api/health")
async def health_api():
    return {"status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Mount static files LAST (lower precedence)
# Serve CSS files
app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")

# Serve JS files
app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")

# Serve image files
app.mount("/img", StaticFiles(directory=str(frontend_dir / "img")), name="img")

# Serve HTML files (root) - LAST to avoid conflicts
app.mount("/", StaticFiles(directory=str(frontend_dir / "html"), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
