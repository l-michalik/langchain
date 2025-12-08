from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import chat


load_dotenv()


def create_app() -> FastAPI:
    config: FastAPIConfig = {
        "title": "AI-CHATBOT-AGENT",
        "description": "Joule AI Chatbot Agent",
        "version": "1.0.0",
    }

    app = FastAPI(**config)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["set-cookie"],
    )

    app.include_router(chat.router,     prefix="/api/chat",    tags=["chat"])

    return app


app = create_app()
