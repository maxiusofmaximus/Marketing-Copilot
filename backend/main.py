"""
Marketing Copilot Backend - CloudLabs Hackathon Talento Tech 2026
"""
from dotenv import load_dotenv
load_dotenv(override=True)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analytics, chat, dashboard
from app.services.data_loader import DataLoader

app = FastAPI(
    title="Marketing Copilot API",
    description="Co-piloto de Marketing impulsado por análisis de datos e IA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Data loader global ───────────────────────────────────────
data_loader = DataLoader()


@app.on_event("startup")
async def startup_event():
    data_loader.load_data()
    print("=" * 60)
    print("✅ Marketing Copilot API lista")
    print(f"   Recordings: {len(data_loader.recordings)} filas")
    print(f"   Metrics:    {len(data_loader.metrics)} filas")
    print(f"   Usuarios:   {data_loader.total_sessions()}")
    print("=" * 60)


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
