import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Primetrade Assignment API", version="1.0.0")

# Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://app.example.com".
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Primetrade API is running"}
