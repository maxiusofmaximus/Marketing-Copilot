"""
Router del Chat - Endpoint principal del Co-piloto.
"""

from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse, ChartData
from app.services.analytics_engine import AnalyticsEngine
from app.services.llm_service import LLMService

router = APIRouter()
_llm_service: LLMService = None


def get_engine() -> AnalyticsEngine:
    from main import data_loader
    return AnalyticsEngine(data_loader.recordings, data_loader.metrics)


def get_llm() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


@router.post("/ask", response_model=AskResponse)
async def ask_copilot(request: AskRequest):
    """
    Endpoint principal del Co-piloto.
    Recibe pregunta en lenguaje natural → devuelve respuesta + interpretación + gráfico.
    """
    engine = get_engine()
    llm = get_llm()

    # 1. Motor analítico interpreta la pregunta
    result = engine.answer_question(request.question)

    # 2. LLM enriquece con interpretación de negocio
    interpretation = await llm.generate_interpretation(
        question=request.question,
        analytics_answer=result["answer"],
        raw_data=result.get("data", {}),
    )

    # 3. Preparar gráfico si hay datos
    chart_data = None
    if result.get("chart"):
        c = result["chart"]
        chart_data = ChartData(
            chart_type=c["type"],
            labels=c["labels"],
            values=c["values"],
            label=c.get("label", ""),
        )

    return AskResponse(
        answer=result["answer"],
        interpretation=interpretation,
        chart_data=chart_data,
    )


@router.get("/suggested-questions")
async def suggested_questions():
    return {
        "questions": [
            "¿Cuál fue la página más visitada?",
            "¿Dónde abandonan más los usuarios?",
            "¿Cuál es el flujo de navegación más común?",
            "¿Cuál fue el producto más consultado?",
            "¿Cómo es la interacción promedio por página?",
            "¿Qué patrones de conversión hay hacia pricing?",
            "¿Desde qué dispositivos nos visitan más?",
            "¿Qué páginas atraen tráfico pero no retienen?",
            "¿Hay problemas de frustración en el sitio?",
            "¿A qué hora hay más tráfico?",
            "Dame un resumen general del sitio",
        ]
    }
