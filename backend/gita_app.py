"""Small preview entrypoint for the scripture companion API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.gita_api import router

app = FastAPI(title="Bhagavad Gita Companion API", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*$",
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(router, prefix="/api")
