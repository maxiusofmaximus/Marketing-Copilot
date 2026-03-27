# Marketing Copilot — CloudLabs Hackathon Talento Tech 2026

Co-piloto de Marketing impulsado por análisis de datos e Inteligencia Artificial. Analiza el comportamiento de usuarios en la plataforma CloudLabs Learning y genera recomendaciones accionables en lenguaje natural.

---

## ¿Qué hace el proyecto?

El usuario escribe una pregunta en lenguaje natural (por ejemplo: *"¿Dónde abandonan más los usuarios?"*) y el sistema responde con:

- **Datos concretos** calculados sobre el dataset real de Microsoft Clarity
- **Interpretación de negocio** generada por IA (Groq / Cerebras / Claude / Gemini / OpenAI)
- **Gráfico visual** cuando aplica (barras, líneas, pie)

---

## Arquitectura

```text
marketing-copilot-cloudlabs/
├── backend/          → API REST con FastAPI (Python)
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
│   ├── data/
│   │   ├── 1_Data_Recordings.csv   ← sesiones de usuarios
│   │   └── 2_Data_Metrics.csv      ← métricas de comportamiento
│   └── app/
│       ├── routers/
│       │   ├── chat.py             ← endpoint /api/ask (copilot)
│       │   ├── analytics.py        ← endpoints de análisis
│       │   └── dashboard.py        ← resumen general
│       ├── services/
│       │   ├── analytics_engine.py ← motor de análisis con pandas
│       │   ├── llm_service.py      ← integración con LLMs
│       │   └── data_loader.py      ← carga de CSVs
│       └── models/
│           └── schemas.py          ← modelos Pydantic
└── frontend/         → SPA con Angular 17
    └── src/app/
        ├── components/
        │   ├── copilot/    ← chat con IA
        │   ├── dashboard/  ← KPIs generales
        │   ├── analytics/  ← tablas de análisis
        │   ├── chart/      ← gráficos con Chart.js
        │   ├── kpi-card/   ← tarjetas de métricas
        │   └── sidebar/    ← navegación
        └── services/
            ├── api.service.ts
            └── analytics.service.ts
```

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Angular 17, Chart.js, TypeScript |
| Backend | FastAPI, Python 3.11 |
| Análisis de datos | Pandas, NumPy |
| IA / LLM | Groq (llama-3.3-70b), Cerebras, Claude, Gemini, OpenAI |
| Dataset | Microsoft Clarity — CloudLabs Learning |

---

## Instalación y Ejecución

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

API disponible en: `http://localhost:8000`
Documentación interactiva: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
ng serve
```

App disponible en: `http://localhost:4200`

---

## Configuración del LLM (backend/.env)

El sistema funciona sin LLM (devuelve los datos del motor analítico). Para activar la interpretación de IA, configura uno de los siguientes proveedores en `backend/.env`:

```env
# Groq — gratuito, 14,400 requests/día
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
# Obtener key: https://console.groq.com

# Cerebras — gratuito, muy rápido
LLM_PROVIDER=cerebras
CEREBRAS_API_KEY=csk_...
# Obtener key: https://cloud.cerebras.ai

# Claude (Anthropic)
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...

# Gemini (Google)
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

---

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/ask` | Pregunta al copilot en lenguaje natural |
| GET | `/api/suggested-questions` | Preguntas sugeridas |
| GET | `/api/dashboard` | Resumen general KPIs |
| GET | `/api/analytics/top-pages` | Páginas más visitadas |
| GET | `/api/analytics/abandono` | Puntos de abandono |
| GET | `/api/analytics/flujos` | Flujos de navegación |
| GET | `/api/analytics/conversion` | Patrones de conversión |
| GET | `/api/analytics/segmentation` | Segmentación dispositivo/país |
| GET | `/api/analytics/frustration` | Análisis de frustración |
| GET | `/api/health` | Estado del servidor |

---

## Insights del Motor Analítico

El `AnalyticsEngine` detecta automáticamente la intención de la pregunta y ejecuta el análisis correspondiente:

1. **Páginas Top** — ranking de páginas de entrada por sesiones
2. **Puntos de abandono** — páginas con mayor tasa de salida y bounce
3. **Flujos de navegación** — pares entrada→salida más frecuentes
4. **Interacción por página** — clics, tiempo, engagement promedio
5. **Patrones de conversión** — sesiones que llegaron a pricing / demo / contacto
6. **Segmentación** — distribución por dispositivo, país, navegador, OS
7. **Páginas trampa** — alto tráfico pero bajo engagement
8. **Análisis de frustración** — rage clicks, dead clicks, abandono rápido

---

## Dataset

Los datos provienen de **Microsoft Clarity** sobre la plataforma [CloudLabs Learning](https://cloudlabs.com):

- `1_Data_Recordings.csv` — sesiones individuales de usuarios con URL de entrada/salida, dispositivo, duración, engagement, etc.
- `2_Data_Metrics.csv` — métricas agregadas por página incluyendo DeadClicks, RageClicks, ScrollDepth, etc.

---

## Equipo

Desarrollado para el **Hackathon Talento Tech 2026** — CloudLabs Learning.
