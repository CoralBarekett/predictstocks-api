from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from loguru import logger
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure loguru logger
logger.add("logs/predictstocks.log", rotation="1 MB", enqueue=True)

app = FastAPI(title="PredictStocks API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)