"""
Router del Dashboard - Resumen ejecutivo completo.
"""

from fastapi import APIRouter
from app.services.analytics_engine import AnalyticsEngine

router = APIRouter()


def get_engine() -> AnalyticsEngine:
    from main import data_loader
    return AnalyticsEngine(data_loader.recordings, data_loader.metrics)


@router.get("/dashboard")
async def dashboard():
    """Retorna todos los datos del dashboard en un solo request."""
    engine = get_engine()
    return {
        "summary": engine.get_dashboard_summary(),
        "top_pages": engine.get_top_pages(10),
        "abandono": engine.get_abandono(10),
        "flujos": engine.get_flujos(5),
        "interaccion": engine.get_interaccion(10),
        "conversion": engine.get_conversion(),
        "segmentation": engine.get_segmentation(),
        "trap_pages": engine.get_trap_pages(5),
        "frustration": engine.get_frustration_analysis(),
        "engagement_hourly": engine.get_engagement_by_hour(),
    }
