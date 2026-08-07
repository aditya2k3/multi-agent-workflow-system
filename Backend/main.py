from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager

from Backend.api.meetings import router as meeting_router
from Backend.api.upload import router as upload_router
from Backend.api.analysis import router as analysis_router
from Backend.api.schedule import router as schedule_router
from Backend.api.email import router as email_router
from Backend.api.router import router as router_router
from Backend.database.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown: cleanup if needed


app = FastAPI(title="Enterprise AI Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_router)
app.include_router(meeting_router)
app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(schedule_router)
app.include_router(email_router)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")