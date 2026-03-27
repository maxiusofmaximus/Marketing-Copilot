"""
Marketing Copilot Backend - CloudLabs Hackathon Talento Tech 2026
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv(override=True)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analytics, chat, dashboard
from app.services.data_loader import DataLoader

# ─── Data loader global ───────────────────────────────────────
data_loader = DataLoader()


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_loader.load_data()
    print("=" * 60)
    print("✅ Marketing Copilot API lista")
    print(f"   Recordings: {len(data_loader.recordings)} filas")
    print(f"   Metrics:    {len(data_loader.metrics)} filas")
    print(f"   Usuarios:   {data_loader.total_sessions()}")
    print("=" * 60)
    yield


app = FastAPI(
    title="Marketing Copilot API",
    description="Co-piloto de Marketing impulsado por análisis de datos e IA",
    version="1.0.0",
    lifespan=lifespan,
)

# Orígenes permitidos: en producción fija FRONTEND_ORIGIN (ej. https://tu-app.vercel.app)
_origins = os.getenv("FRONTEND_ORIGIN", "").strip()
if _origins:
    _cors = [o.strip() for o in _origins.split(",") if o.strip()]
    _cred = True
else:
    _cors = ["*"]
    _cred = False  # * + credentials no es válido en Starlette

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=_cred,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(chat.router, prefix="/api", tags=["Chat / Copilot"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])


@app.get("/")
async def root():
    return {"message": "Marketing Copilot API - CloudLabs", "docs": "/docs", "status": "running"}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "dataset_loaded": data_loader.is_loaded,
        "recordings_rows": len(data_loader.recordings),
        "metrics_rows": len(data_loader.metrics),
    }
