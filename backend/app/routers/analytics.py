"""
Router de Analytics - Endpoints para cada tipo de insight.
"""

from fastapi import APIRouter, Query
from app.services.analytics_engine import AnalyticsEngine

router = APIRouter()


def get_engine() -> AnalyticsEngine:
    from main import data_loader
    return AnalyticsEngine(data_loader.recordings, data_loader.metrics)


@router.get("/pages/top")
async def top_pages(limit: int = Query(10, ge=1, le=50)):
    return {"data": get_engine().get_top_pages(limit), "insight": "top_pages"}


@router.get("/abandono")
async def abandono(limit: int = Query(10, ge=1, le=50)):
    return {"data": get_engine().get_abandono(limit), "insight": "abandono"}


@router.get("/flujos")
async def flujos(limit: int = Query(10, ge=1, le=50)):
    return {"data": get_engine().get_flujos(limit), "insight": "flujos"}


@router.get("/interaccion")
async def interaccion(limit: int = Query(15, ge=1, le=50)):
    return {"data": get_engine().get_interaccion(limit), "insight": "interaccion"}


@router.get("/conversion")
async def conversion():
    return {"data": get_engine().get_conversion(), "insight": "conversion"}


@router.get("/segmentation")
async def segmentation():
    return {"data": get_engine().get_segmentation(), "insight": "segmentation"}


@router.get("/trap-pages")
async def trap_pages(limit: int = Query(10, ge=1, le=50)):
    return {"data": get_engine().get_trap_pages(limit), "insight": "trap_pages"}


@router.get("/frustration")
async def frustration(limit: int = Query(10, ge=1, le=50)):
    return {"data": get_engine().get_frustration_analysis(limit), "insight": "frustration"}


@router.get("/engagement-hourly")
async def engagement_hourly():
    return {"data": get_engine().get_engagement_by_hour(), "insight": "engagement_hourly"}


@router.get("/dataset/info")
async def dataset_info():
    from main import data_loader
    return {
        "columns": data_loader.get_columns(),
        "recordings_rows": len(data_loader.recordings),
        "metrics_rows": len(data_loader.metrics),
        "total_users": data_loader.total_sessions(),
    }
