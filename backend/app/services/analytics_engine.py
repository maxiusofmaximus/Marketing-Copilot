"""
Analytics Engine - Motor de análisis adaptado al dataset REAL de CloudLabs/Clarity.
===================================================================================

COLUMNAS REALES DE RECORDINGS:
  fecha, hora, duracion_sesion, direccion_url_entrada, direccion_url_salida,
  referente, id_usuario_clarity, explorador, dispositivo, sistema_operativo,
  pais, recuento_paginas, clics_sesion, duracion_sesion_segundos,
  abandono_rapido, clicks_por_pagina, tiempo_por_pagina, interaccion_total,
  posible_frustracion, standarized_engagement_score, entrada_es_home,
  trafico_externo, direccion_url_entrada_clean, direccion_url_salida_clean

COLUMNAS REALES DE METRICS:
  sessionsCount, sessionsWithMetricPercentage, sessionsWithoutMetricPercentage,
  pagesViews, subTotal, Url, Device, OS, metricName, averageScrollDepth,
  totalSessionCount, totalBotSessionCount, distinctUserCount,
  pagesPerSessionPercentage, totalTime, activeTime, url_clean

INSIGHTS:
  1. Páginas/Productos Top
  2. Puntos Críticos de Abandono
  3. Flujos de Navegación (entrada → salida)
  4. Interacción Promedio por Página
  5. Patrones de Conversión hacia páginas clave
  6. [EXTRA] Segmentación por dispositivo/país/navegador
  7. [EXTRA] Páginas trampa (alto tráfico, bajo engagement)
  8. [EXTRA] Análisis de frustración y rage clicks
"""

import pandas as pd
import numpy as np
from typing import Optional


class AnalyticsEngine:
    """Ejecuta todos los cálculos analíticos sobre los DataFrames reales."""

    # Páginas de alto interés para conversión
    CONVERSION_KEYWORDS = ["pricing", "request-demo", "contact", "demo", "precios", "registro"]

    def __init__(self, recordings: pd.DataFrame, metrics: pd.DataFrame = None):
        self.rec = recordings
        self.met = metrics if metrics is not None else pd.DataFrame()

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 1: Páginas Top (por visitas de entrada)
    # ═══════════════════════════════════════════════════════════

    def get_top_pages(self, limit: int = 10) -> list[dict]:
        """
        Ranking de páginas más visitadas como punto de entrada.
        Usa direccion_url_entrada_clean.
        """
        col = "direccion_url_entrada_clean"
        if col not in self.rec.columns:
            return []

        page_counts = self.rec[col].value_counts().head(limit).reset_index()
        page_counts.columns = ["page", "sessions"]
        total = len(self.rec)
        page_counts["percentage"] = (page_counts["sessions"] / total * 100).round(2)

        # Agregar métricas promedio por página
        if "standarized_engagement_score" in self.rec.columns:
            eng = self.rec.groupby(col)["standarized_engagement_score"].mean()
            page_counts["avg_engagement"] = page_counts["page"].map(eng).round(3)

        if "duracion_sesion_segundos" in self.rec.columns:
            dur = self.rec.groupby(col)["duracion_sesion_segundos"].mean()
            page_counts["avg_duration_sec"] = page_counts["page"].map(dur).round(1)

        return page_counts.to_dict("records")

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 2: Puntos Críticos de Abandono
    # ═══════════════════════════════════════════════════════════

    def get_abandono(self, limit: int = 10) -> list[dict]:
        """
        Páginas donde más terminan las sesiones (URL de salida).
        Cruza con tasa de abandono rápido.
        """
        col_exit = "direccion_url_salida_clean"
        col_entry = "direccion_url_entrada_clean"

        if col_exit not in self.rec.columns:
            return []

        # Contar salidas por página
        exit_counts = self.rec[col_exit].value_counts().reset_index()
        exit_counts.columns = ["page", "exit_count"]

        # Total de veces que la página fue visitada (como entrada o salida)
        entry_counts = self.rec[col_entry].value_counts().reset_index()
        entry_counts.columns = ["page", "entry_count"]

        result = exit_counts.merge(entry_counts, on="page", how="left")
        result["entry_count"] = result["entry_count"].fillna(0)
        result["total_appearances"] = result["exit_count"] + result["entry_count"]
        result["exit_rate"] = (result["exit_count"] / result["total_appearances"] * 100).round(2)

        # Agregar tasa de abandono rápido para esa página
        if "abandono_rapido" in self.rec.columns:
            bounce = self.rec.groupby(col_exit)["abandono_rapido"].mean() * 100
            result["bounce_rate"] = result["page"].map(bounce).round(2)

        result = result.sort_values("exit_count", ascending=False).head(limit)
        return result.to_dict("records")

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 3: Flujos de Navegación (entrada → salida)
    # ═══════════════════════════════════════════════════════════

    def get_flujos(self, limit: int = 10) -> list[dict]:
        """
        Secuencias entrada→salida más frecuentes.
        Como cada fila es una sesión con URL entrada y salida,
        el flujo es el par (entrada, salida).
        """
        col_in = "direccion_url_entrada_clean"
        col_out = "direccion_url_salida_clean"

        if col_in not in self.rec.columns or col_out not in self.rec.columns:
            return []

        # Crear pares de flujo
        flows = self.rec[[col_in, col_out]].copy()
        flows.columns = ["entrada", "salida"]

        # Excluir flujos donde entrada == salida (single page sessions)
        flows_diff = flows[flows["entrada"] != flows["salida"]]

        if flows_diff.empty:
            flows_diff = flows  # fallback

        flow_counts = (
            flows_diff.groupby(["entrada", "salida"])
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(limit)
        )

        total = len(flows_diff)
        flow_counts["percentage"] = (flow_counts["count"] / total * 100).round(2)

        result = []
        for _, row in flow_counts.iterrows():
            result.append({
                "sequence": [row["entrada"], row["salida"]],
                "entrada": row["entrada"],
                "salida": row["salida"],
                "count": int(row["count"]),
                "percentage": float(row["percentage"]),
            })

        return result

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 4: Interacción Promedio por Página
    # ═══════════════════════════════════════════════════════════

    def get_interaccion(self, limit: int = 15) -> list[dict]:
        """
        Métricas promedio de interacción por página de entrada.
        """
        col = "direccion_url_entrada_clean"
        if col not in self.rec.columns:
            return []

        agg_dict = {"sessions": (col, "count")}

        metric_cols = {
            "avg_clicks_session": ("clics_sesion", "mean"),
            "avg_clicks_page": ("clicks_por_pagina", "mean"),
            "avg_time_page": ("tiempo_por_pagina", "mean"),
            "avg_duration": ("duracion_sesion_segundos", "mean"),
            "avg_interaction": ("interaccion_total", "mean"),
            "avg_engagement": ("standarized_engagement_score", "mean"),
            "avg_pages": ("recuento_paginas", "mean"),
        }

        for key, (source_col, func) in metric_cols.items():
            if source_col in self.rec.columns:
                agg_dict[key] = (source_col, func)

        result = self.rec.groupby(col).agg(**agg_dict).reset_index()
        result = result.rename(columns={col: "page"})

        # Redondear
        for c in result.columns:
            if c.startswith("avg_"):
                result[c] = result[c].round(2)

        result = result.sort_values("sessions", ascending=False).head(limit)
        return result.to_dict("records")

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 5: Patrones de Conversión
    # ═══════════════════════════════════════════════════════════

    def get_conversion(self) -> list[dict]:
        """
        Analiza sesiones que llegaron a páginas clave (pricing, demo, contact).
        ¿De dónde vienen? ¿Cuál es su engagement? ¿Cuánto duran?
        """
        col_entry = "direccion_url_entrada_clean"
        col_exit = "direccion_url_salida_clean"

        if col_entry not in self.rec.columns:
            return []

        total_sessions = len(self.rec)
        results = []

        for keyword in self.CONVERSION_KEYWORDS:
            # Sesiones donde la página de entrada O salida contiene el keyword
            mask = (
                self.rec[col_entry].str.contains(keyword, case=False, na=False) |
                self.rec[col_exit].str.contains(keyword, case=False, na=False)
            )
            subset = self.rec[mask]

            if subset.empty:
                continue

            sessions_count = len(subset)
            reach_rate = round(sessions_count / total_sessions * 100, 2)

            info = {
                "conversion_page": keyword,
                "sessions_reached": sessions_count,
                "total_sessions": total_sessions,
                "reach_rate": reach_rate,
            }

            # ¿De dónde vienen? (referentes)
            if "referente" in subset.columns:
                refs = subset["referente"].value_counts().head(5)
                info["top_referrers"] = [
                    {"source": str(k), "count": int(v)}
                    for k, v in refs.items()
                ]

            # ¿Desde qué página de entrada llegan?
            if col_entry in subset.columns:
                entries = subset[col_entry].value_counts().head(5)
                info["top_entry_pages"] = [
                    {"page": str(k), "count": int(v)}
                    for k, v in entries.items()
                ]

            # Métricas promedio de estas sesiones
            if "standarized_engagement_score" in subset.columns:
                info["avg_engagement"] = round(float(subset["standarized_engagement_score"].mean()), 3)
            if "duracion_sesion_segundos" in subset.columns:
                info["avg_duration"] = round(float(subset["duracion_sesion_segundos"].mean()), 1)
            if "abandono_rapido" in subset.columns:
                info["bounce_rate"] = round(float(subset["abandono_rapido"].mean() * 100), 2)

            results.append(info)

        return results

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 6 [EXTRA]: Segmentación
    # ═══════════════════════════════════════════════════════════

    def get_segmentation(self) -> dict:
        """Distribución por dispositivo, país, navegador y OS."""
        result = {}

        for col, key in [
            ("dispositivo", "by_device"),
            ("pais", "by_country"),
            ("explorador", "by_browser"),
            ("sistema_operativo", "by_os"),
        ]:
            if col in self.rec.columns:
                counts = self.rec[col].value_counts().head(10)
                result[key] = [
                    {"name": str(k), "count": int(v), "percentage": round(v / len(self.rec) * 100, 2)}
                    for k, v in counts.items()
                ]

        # Tráfico externo vs directo
        if "trafico_externo" in self.rec.columns:
            ext = self.rec["trafico_externo"].sum()
            result["traffic_source"] = {
                "external": int(ext),
                "direct": int(len(self.rec) - ext),
                "external_pct": round(float(ext / len(self.rec) * 100), 2),
            }

        return result

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 7 [EXTRA]: Páginas Trampa (tráfico alto, engagement bajo)
    # ═══════════════════════════════════════════════════════════

    def get_trap_pages(self, limit: int = 10) -> list[dict]:
        """
        Páginas que atraen mucho tráfico pero tienen bajo engagement
        y alta tasa de abandono rápido.
        """
        col = "direccion_url_entrada_clean"
        if col not in self.rec.columns:
            return []

        agg = {"sessions": (col, "count")}
        if "standarized_engagement_score" in self.rec.columns:
            agg["avg_engagement"] = ("standarized_engagement_score", "mean")
        if "abandono_rapido" in self.rec.columns:
            agg["bounce_rate"] = ("abandono_rapido", "mean")
        if "duracion_sesion_segundos" in self.rec.columns:
            agg["avg_duration"] = ("duracion_sesion_segundos", "mean")

        pages = self.rec.groupby(col).agg(**agg).reset_index()
        pages = pages.rename(columns={col: "page"})

        # Solo páginas con tráfico significativo (arriba de mediana)
        median_sessions = pages["sessions"].median()
        pages = pages[pages["sessions"] >= median_sessions].copy()

        if pages.empty:
            return []

        # Trap score: alto bounce + bajo engagement = trampa
        if "bounce_rate" in pages.columns and "avg_engagement" in pages.columns:
            # Normalizar engagement a 0-1 (donde 0 es peor)
            eng_min = pages["avg_engagement"].min()
            eng_max = pages["avg_engagement"].max()
            eng_range = eng_max - eng_min if eng_max != eng_min else 1
            pages["eng_normalized"] = 1 - ((pages["avg_engagement"] - eng_min) / eng_range)
            pages["trap_score"] = (pages["bounce_rate"] * 0.5 + pages["eng_normalized"] * 0.5).round(3)
        elif "bounce_rate" in pages.columns:
            pages["trap_score"] = pages["bounce_rate"].round(3)
        else:
            pages["trap_score"] = 0.5

        for c in pages.columns:
            if pages[c].dtype in ["float64", "float32"]:
                pages[c] = pages[c].round(3)

        pages = pages.sort_values("trap_score", ascending=False).head(limit)
        return pages.to_dict("records")

    # ═══════════════════════════════════════════════════════════
    # INSIGHT 8 [EXTRA]: Frustración y Rage Clicks (desde Metrics)
    # ═══════════════════════════════════════════════════════════

    def get_frustration_analysis(self, limit: int = 10) -> dict:
        """
        Usa 2_Data_Metrics.csv para analizar DeadClicks, RageClicks,
        y otros indicadores de frustración por página.
        """
        if self.met.empty or "metricName" not in self.met.columns:
            # Fallback: usar posible_frustracion de recordings
            if "posible_frustracion" in self.rec.columns:
                col = "direccion_url_entrada_clean"
                if col in self.rec.columns:
                    frust = self.rec[self.rec["posible_frustracion"] == True]
                    pages = frust[col].value_counts().head(limit)
                    return {
                        "source": "recordings",
                        "frustrated_sessions": int(len(frust)),
                        "total_sessions": int(len(self.rec)),
                        "frustration_rate": round(len(frust) / len(self.rec) * 100, 2),
                        "top_frustrated_pages": [
                            {"page": str(k), "count": int(v)}
                            for k, v in pages.items()
                        ],
                    }
            return {}

        result = {"source": "metrics", "by_metric": {}}

        # Analizar cada tipo de métrica de frustración
        for metric_name in ["DeadClickCount", "RageClickCount", "ExcessiveScrollCount", "QuickBackCount"]:
            subset = self.met[self.met["metricName"] == metric_name]
            if subset.empty:
                continue

            # Top páginas afectadas
            if "url_clean" in subset.columns:
                top_pages = (
                    subset.groupby("url_clean")
                    .agg(
                        total_sessions=("sessionsCount", "sum"),
                        affected_pct=("sessionsWithMetricPercentage", "mean"),
                        subtotal=("subTotal", "sum"),
                    )
                    .sort_values("subtotal", ascending=False)
                    .head(limit)
                    .reset_index()
                )

                for c in top_pages.columns:
                    if top_pages[c].dtype in ["float64", "float32"]:
                        top_pages[c] = top_pages[c].round(2)

                result["by_metric"][metric_name] = top_pages.to_dict("records")

        return result

    # ═══════════════════════════════════════════════════════════
    # DASHBOARD - Resumen General
    # ═══════════════════════════════════════════════════════════

    def get_dashboard_summary(self) -> dict:
        """Métricas resumen para el dashboard principal."""
        r = self.rec
        total = len(r)

        summary = {"total_sessions": total}

        if "id_usuario_clarity" in r.columns:
            summary["unique_users"] = int(r["id_usuario_clarity"].nunique())

        if "recuento_paginas" in r.columns:
            summary["avg_pages_per_session"] = round(float(r["recuento_paginas"].mean()), 2)

        if "duracion_sesion_segundos" in r.columns:
            summary["avg_duration_seconds"] = round(float(r["duracion_sesion_segundos"].mean()), 1)

        if "standarized_engagement_score" in r.columns:
            summary["avg_engagement_score"] = round(float(r["standarized_engagement_score"].mean()), 4)

        if "abandono_rapido" in r.columns:
            bounces = r["abandono_rapido"].sum()
            summary["bounce_rate"] = round(float(bounces / total * 100), 2)
            summary["bounced_sessions"] = int(bounces)

        if "clics_sesion" in r.columns:
            summary["avg_clicks_per_session"] = round(float(r["clics_sesion"].mean()), 2)

        if "posible_frustracion" in r.columns:
            frust = r["posible_frustracion"].sum()
            summary["frustration_rate"] = round(float(frust / total * 100), 2)

        if "entrada_es_home" in r.columns:
            home = r["entrada_es_home"].sum()
            summary["home_entry_rate"] = round(float(home / total * 100), 2)

        if "trafico_externo" in r.columns:
            ext = r["trafico_externo"].sum()
            summary["external_traffic_rate"] = round(float(ext / total * 100), 2)

        if "fecha" in r.columns:
            summary["date_range"] = {
                "start": str(r["fecha"].min()),
                "end": str(r["fecha"].max()),
            }

        return summary

    # ═══════════════════════════════════════════════════════════
    # Engagement por hora del día
    # ═══════════════════════════════════════════════════════════

    def get_engagement_by_hour(self) -> list[dict]:
        """Engagement y sesiones por hora del día."""
        if "hora" not in self.rec.columns:
            return []

        df = self.rec.copy()
        # Extraer hora (viene como "10:49")
        df["hour"] = df["hora"].astype(str).str.split(":").str[0]
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce")

        agg = {"sessions": ("hour", "count")}
        if "standarized_engagement_score" in df.columns:
            agg["avg_engagement"] = ("standarized_engagement_score", "mean")
        if "duracion_sesion_segundos" in df.columns:
            agg["avg_duration"] = ("duracion_sesion_segundos", "mean")
        if "abandono_rapido" in df.columns:
            agg["bounce_rate"] = ("abandono_rapido", "mean")

        hourly = df.groupby("hour").agg(**agg).reset_index()

        for c in hourly.columns:
            if hourly[c].dtype in ["float64", "float32"]:
                hourly[c] = hourly[c].round(3)

        if "bounce_rate" in hourly.columns:
            hourly["bounce_rate"] = (hourly["bounce_rate"] * 100).round(2)

        return hourly.sort_values("hour").to_dict("records")

    # ═══════════════════════════════════════════════════════════
    # RESPONDER PREGUNTAS (para el endpoint /ask)
    # ═══════════════════════════════════════════════════════════

    def answer_question(self, question: str) -> dict:
        """
        Dada una pregunta en texto, ejecuta el análisis correspondiente.
        """
        q = question.lower()

        if any(w in q for w in ["más vista", "más visitada", "top página", "top pagina", "más tráfico", "ranking página", "página más"]):
            data = self.get_top_pages(5)
            if data:
                top = data[0]
                return {
                    "intent": "top_pages",
                    "data": data,
                    "answer": f"La página más visitada es '{top['page']}' con {top['sessions']} sesiones ({top['percentage']}% del total). Duración promedio: {top.get('avg_duration_sec', 'N/A')}s.",
                    "chart": {"type": "horizontal_bar", "labels": [d["page"] for d in data], "values": [d["sessions"] for d in data], "label": "Sesiones"},
                }

        if any(w in q for w in ["producto", "más consultado", "más visto"]):
            data = self.get_top_pages(5)
            if data:
                top = data[0]
                return {
                    "intent": "top_pages",
                    "data": data,
                    "answer": f"La página/producto más consultado es '{top['page']}' con {top['sessions']} sesiones ({top['percentage']}% del total).",
                    "chart": {"type": "horizontal_bar", "labels": [d["page"] for d in data], "values": [d["sessions"] for d in data], "label": "Sesiones"},
                }

        if any(w in q for w in ["abandono", "salida", "abandonan", "exit", "bounce", "rebote"]):
            data = self.get_abandono(5)
            if data:
                top = data[0]
                return {
                    "intent": "abandono",
                    "data": data,
                    "answer": f"La página con más abandonos es '{top['page']}' con {top['exit_count']} salidas (tasa: {top.get('exit_rate', 'N/A')}%). Bounce rate: {top.get('bounce_rate', 'N/A')}%.",
                    "chart": {"type": "bar", "labels": [d["page"] for d in data], "values": [d["exit_count"] for d in data], "label": "Salidas"},
                }

        if any(w in q for w in ["flujo", "recorrido", "navegación", "secuencia", "camino", "ruta"]):
            data = self.get_flujos(5)
            if data:
                top = data[0]
                return {
                    "intent": "flujos",
                    "data": data,
                    "answer": f"El flujo más frecuente es: {top['entrada']} → {top['salida']} ({top['count']} sesiones, {top['percentage']}% del total).",
                    "chart": None,
                }

        if any(w in q for w in ["interacción", "interaccion", "engagement", "clics", "clicks", "tiempo"]):
            data = self.get_interaccion(5)
            if data:
                return {
                    "intent": "interaccion",
                    "data": data,
                    "answer": f"'{data[0]['page']}' lidera con {data[0]['sessions']} sesiones, {data[0].get('avg_clicks_session', 'N/A')} clics promedio y {data[0].get('avg_duration', 'N/A')}s de duración promedio.",
                    "chart": None,
                }

        if any(w in q for w in ["conversión", "conversion", "pricing", "demo", "contacto"]):
            data = self.get_conversion()
            if data:
                return {
                    "intent": "conversion",
                    "data": data,
                    "answer": "Análisis de conversión: " + "; ".join([
                        f"'{d['conversion_page']}' alcanzada por {d['reach_rate']}% de sesiones"
                        for d in data
                    ]),
                    "chart": {"type": "bar", "labels": [d["conversion_page"] for d in data], "values": [d["reach_rate"] for d in data], "label": "Tasa de alcance (%)"},
                }

        if any(w in q for w in ["dispositivo", "device", "móvil", "celular", "pc", "país", "pais", "navegador"]):
            data = self.get_segmentation()
            parts = []
            if "by_device" in data:
                parts.append("Por dispositivo: " + ", ".join([f"{d['name']}: {d['count']} ({d['percentage']}%)" for d in data["by_device"][:3]]))
            if "by_country" in data:
                parts.append("Por país: " + ", ".join([f"{d['name']}: {d['count']} ({d['percentage']}%)" for d in data["by_country"][:3]]))
            return {
                "intent": "segmentation",
                "data": data,
                "answer": ". ".join(parts) if parts else "No hay datos de segmentación.",
                "chart": None,
            }

        if any(w in q for w in ["trampa", "no retiene", "alto tráfico bajo", "atrae pero"]):
            data = self.get_trap_pages(5)
            if data:
                return {
                    "intent": "trap_pages",
                    "data": data,
                    "answer": "Páginas con alto tráfico pero bajo engagement: " + ", ".join([
                        f"'{d['page']}' (trap: {d.get('trap_score', 0)}, bounce: {d.get('bounce_rate', 0):.0%})"
                        for d in data[:3]
                    ]),
                    "chart": None,
                }

        if any(w in q for w in ["frustración", "frustracion", "rage", "dead click", "problema"]):
            data = self.get_frustration_analysis()
            if data:
                answer = f"Tasa de frustración: {data.get('frustration_rate', 'N/A')}% de las sesiones."
                if "top_frustrated_pages" in data:
                    answer += " Páginas más afectadas: " + ", ".join([
                        f"'{p['page']}' ({p['count']} sesiones)"
                        for p in data["top_frustrated_pages"][:3]
                    ])
                return {
                    "intent": "frustration",
                    "data": data,
                    "answer": answer,
                    "chart": None,
                }

        if any(w in q for w in ["hora", "horario", "cuándo", "cuando", "mejor momento"]):
            data = self.get_engagement_by_hour()
            if data:
                best = max(data, key=lambda x: x.get("sessions", 0))
                return {
                    "intent": "hourly",
                    "data": data,
                    "answer": f"La hora con más tráfico es las {int(best['hour'])}:00 con {best['sessions']} sesiones. Engagement promedio: {best.get('avg_engagement', 'N/A')}.",
                    "chart": {"type": "line", "labels": [f"{int(d['hour'])}:00" for d in data], "values": [d["sessions"] for d in data], "label": "Sesiones"},
                }

        if any(w in q for w in ["resumen", "general", "dashboard", "overview", "cómo va", "estado"]):
            data = self.get_dashboard_summary()
            parts = [f"{data['total_sessions']} sesiones totales"]
            if "unique_users" in data:
                parts.append(f"{data['unique_users']} usuarios únicos")
            if "bounce_rate" in data:
                parts.append(f"tasa de rebote: {data['bounce_rate']}%")
            if "avg_duration_seconds" in data:
                parts.append(f"duración promedio: {data['avg_duration_seconds']}s")
            if "avg_engagement_score" in data:
                parts.append(f"engagement promedio: {data['avg_engagement_score']}")
            return {
                "intent": "summary",
                "data": data,
                "answer": "Resumen: " + ", ".join(parts) + ".",
                "chart": None,
            }

        # Default
        return {
            "intent": "unknown",
            "data": self.get_dashboard_summary(),
            "answer": "No estoy seguro de qué análisis necesitas. Puedo ayudarte con: páginas más visitadas, puntos de abandono, flujos de navegación, interacción por página, patrones de conversión, segmentación por dispositivo/país, páginas trampa, análisis de frustración, o engagement por hora.",
            "chart": None,
        }
