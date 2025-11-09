from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Form Agent API",
    description="Chat with an AI agent that has access to form management database",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    return {
        "message": "Form Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }
