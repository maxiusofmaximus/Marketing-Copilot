"""
Data Loader - Carga, limpieza y normalización del dataset REAL de Microsoft Clarity.
====================================================================================
Dos archivos:
  - 1_Data_Recordings.csv → Sesiones individuales (67K filas)
  - 2_Data_Metrics.csv → Métricas agregadas por segmento (33K filas)
"""

import pandas as pd
import numpy as np
import os
import glob
import re


def _default_data_dir() -> str:
    """Ruta absoluta a backend/data (funciona en local, Docker y Render con cwd distinto)."""
    here = os.path.dirname(os.path.abspath(__file__))
    backend_root = os.path.dirname(os.path.dirname(here))
    return os.path.join(backend_root, "data")


class DataLoader:
    """
    Carga ambos CSVs de Clarity, los limpia y normaliza.
    """

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir if data_dir is not None else _default_data_dir()
        self.recordings: pd.DataFrame = pd.DataFrame()  # Sesiones individuales
        self.metrics: pd.DataFrame = pd.DataFrame()      # Métricas agregadas
        self.is_loaded: bool = False

    def load_data(self):
        """Carga ambos CSVs desde la carpeta data/."""
        self._load_recordings()
        self._load_metrics()
        self.is_loaded = True

    # ══════════════════════════════════════════════════════════
    # RECORDINGS (sesiones individuales)
    # ══════════════════════════════════════════════════════════

    def _load_recordings(self):
        filepath = self._find_file("recording")
        if filepath is None:
            filepath = self._find_file("1_data")
        if filepath is None:
            csvs = glob.glob(os.path.join(self.data_dir, "*.csv"))
            if csvs:
                filepath = max(csvs, key=os.path.getsize)

        if filepath is None:
            print("⚠️  No se encontró 1_Data_Recordings.csv — generando datos de ejemplo")
            self._generate_sample_recordings()
            return

        print(f"📂 Cargando Recordings: {filepath}")
        df = self._read_csv(filepath)
        df = self._clean_recordings(df)
        self.recordings = df
        print(f"   ✅ {len(df)} sesiones cargadas | Columnas: {list(df.columns)}")

    def _clean_recordings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y normaliza el CSV de recordings."""

        # ── Parsear fecha ──────────────────────────────────────
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"], format="mixed", errors="coerce")

        # ── Extraer URL limpia de entrada y salida ─────────────
        for col in ["direccion_url_entrada", "direccion_url_salida"]:
            if col in df.columns:
                df[col + "_clean"] = df[col].apply(self._clean_url)

        # ── Numéricos ─────────────────────────────────────────
        numeric_cols = [
            "duracion_sesion_segundos", "recuento_paginas", "clics_sesion",
            "clicks_por_pagina", "tiempo_por_pagina", "interaccion_total",
            "standarized_engagement_score",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # ── Booleanos (vienen como 0/1) ───────────────────────
        bool_cols = ["abandono_rapido", "posible_frustracion", "entrada_es_home", "trafico_externo"]
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).map({
                    "1": True, "0": False, "1.0": True, "0.0": False,
                    "True": True, "False": False, "true": True, "false": False,
                }).fillna(False)

        # ── Limpiar strings ───────────────────────────────────
        for col in ["dispositivo", "sistema_operativo", "pais", "explorador"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # ── Eliminar filas sin usuario ────────────────────────
        if "id_usuario_clarity" in df.columns:
            df = df[df["id_usuario_clarity"].notna() & (df["id_usuario_clarity"] != "")]

        return df

    @staticmethod
    def _clean_url(url: str) -> str:
        """
        Extrae el path limpio de una URL completa.
        https://cloudlabslearning.com/pricing?foo=bar#hash → /pricing
        """
        if pd.isna(url) or not isinstance(url, str):
            return "/unknown"
        try:
            url = re.sub(r"https?://[^/]+", "", url)
            url = re.split(r"[?#]", url)[0]
            url = url.rstrip("/")
            return url if url else "/"
        except Exception:
            return "/unknown"

    # ══════════════════════════════════════════════════════════
    # METRICS (datos agregados)
    # ══════════════════════════════════════════════════════════

    def _load_metrics(self):
        filepath = self._find_file("metric")
        if filepath is None:
            filepath = self._find_file("2_data")

        if filepath is None:
            print("⚠️  No se encontró 2_Data_Metrics.csv")
            return

        print(f"📂 Cargando Metrics: {filepath}")
        df = self._read_csv(filepath)
        df = self._clean_metrics(df)
        self.metrics = df
        print(f"   ✅ {len(df)} registros de métricas | Tipos: {df['metricName'].unique().tolist() if 'metricName' in df.columns else 'N/A'}")

    def _clean_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia el CSV de métricas agregadas."""
        df.columns = df.columns.str.strip()

        numeric_cols = [
            "sessionsCount", "sessionsWithMetricPercentage",
            "sessionsWithoutMetricPercentage", "pagesViews", "subTotal",
            "averageScrollDepth", "totalSessionCount", "totalBotSessionCount",
            "distinctUserCount", "pagesPerSessionPercentage",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "Url" in df.columns:
            df["url_clean"] = df["Url"].apply(self._clean_url)

        return df

    # ══════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════

    def _find_file(self, keyword: str) -> str | None:
        for f in glob.glob(os.path.join(self.data_dir, "*.csv")):
            if keyword.lower() in os.path.basename(f).lower():
                return f
        return None

    def _read_csv(self, filepath: str) -> pd.DataFrame:
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                return pd.read_csv(filepath, encoding=encoding)
            except (UnicodeDecodeError, Exception):
                continue
        raise ValueError(f"No se pudo leer {filepath}")

    def total_sessions(self) -> int:
        if "id_usuario_clarity" in self.recordings.columns:
            return self.recordings["id_usuario_clarity"].nunique()
        return len(self.recordings)

    def total_rows(self) -> int:
        return len(self.recordings)

    def get_columns(self) -> dict:
        return {
            "recordings": list(self.recordings.columns),
            "metrics": list(self.metrics.columns),
        }

    # ══════════════════════════════════════════════════════════
    # DATOS DE EJEMPLO (fallback)
    # ══════════════════════════════════════════════════════════

    def _generate_sample_recordings(self):
        np.random.seed(42)
        n = 2000
        pages = [
            "https://cloudlabslearning.com/",
            "https://cloudlabslearning.com/pricing",
            "https://cloudlabslearning.com/products",
            "https://cloudlabslearning.com/high-school",
            "https://cloudlabslearning.com/request-demo",
            "https://cloudlabslearning.com/contact",
            "https://cloudlabslearning.com/about-us",
            "https://cloudlabslearning.com/blog",
        ]
        self.recordings = pd.DataFrame({
            "fecha": pd.date_range("2026-03-13", periods=n, freq="2min"),
            "hora": [f"{np.random.randint(8,22)}:{np.random.randint(0,60):02d}" for _ in range(n)],
            "direccion_url_entrada": np.random.choice(pages, n),
            "direccion_url_salida": np.random.choice(pages, n),
            "referente": np.random.choice(["https://www.google.com/", "https://facebook.com/", "(direct)", ""], n),
            "id_usuario_clarity": [f"usr{i:04d}" for i in np.random.randint(0, 800, n)],
            "explorador": np.random.choice(["Chrome", "Firefox", "Safari", "Edge"], n),
            "dispositivo": np.random.choice(["PC", "Mobile", "Tablet"], n, p=[0.5, 0.4, 0.1]),
            "sistema_operativo": np.random.choice(["Windows", "Android", "iOS", "MacOS"], n),
            "pais": np.random.choice(["Colombia", "Mexico", "USA", "Spain", "Peru"], n),
            "recuento_paginas": np.random.randint(1, 8, n),
            "clics_sesion": np.random.randint(0, 20, n),
            "duracion_sesion_segundos": np.random.uniform(3, 600, n).round(1),
            "abandono_rapido": np.random.choice([0, 1], n, p=[0.7, 0.3]),
            "clicks_por_pagina": np.random.uniform(0, 5, n).round(2),
            "tiempo_por_pagina": np.random.uniform(2, 120, n).round(1),
            "interaccion_total": np.random.randint(1, 30, n),
            "posible_frustracion": np.random.choice([0, 1], n, p=[0.85, 0.15]),
            "standarized_engagement_score": np.random.uniform(-1, 2, n).round(4),
            "entrada_es_home": np.random.choice([0, 1], n, p=[0.6, 0.4]),
            "trafico_externo": np.random.choice([0, 1], n, p=[0.5, 0.5]),
        })
        for col in ["direccion_url_entrada", "direccion_url_salida"]:
            self.recordings[col + "_clean"] = self.recordings[col].apply(self._clean_url)
