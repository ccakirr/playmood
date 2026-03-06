import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine
from db import Base  # triggers model registration
from db.models import User, Playlist  # noqa: F401 – ensure tables are created

from routers import playlist_router, youtube_router
from routers.auth_router import router as auth_router

# Create all tables on startup (idempotent)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PlayMood API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(playlist_router.router)
app.include_router(youtube_router.router)