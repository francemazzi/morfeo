from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import data_extraction

app = FastAPI(
    title="Morfeo API",
    description="API per l'estrazione di dati da documenti PDF",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_extraction.router, prefix="/morfeo", tags=["pdf"]) 