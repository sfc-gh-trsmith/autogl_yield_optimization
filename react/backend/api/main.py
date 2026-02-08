import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import assets, predictions, agent, simulation, telemetry
from database import get_connection, close_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_connection()
    yield
    close_connection()

app = FastAPI(
    title="SnowCore Permian Integration API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "snowcore-permian-api"}
