import os
from openai import OpenAI
from services.agent import DjAI
from fastapi import FastAPI
from routers import playlist_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True), name="frontend")

app.include_router(playlist_router.router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)