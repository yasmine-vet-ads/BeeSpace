"""Environmental analytics for BeeSpace MVP dashboards and notebooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EnvironmentalThresholds:
    ndvi_drop_alert: float = -0.12
    ndvi_low: float = 0.42
    temperature_high_c: float = 35.0
    humidity_low_pct: float = 45.0
    acoustic_anomaly_high: float = 0.72
    weight_loss_kg_7d: float = -1.8


def analyze_vegetation_health(ndvi: float, ndwi: float) -> dict[str, object]:
    """Classify vegetation vigor and hydration around the hive."""

    if ndvi >= 0.62 and ndwi >= 0.08:
        status = "saudável"
        risk = "baixo"
        message = "Vegetação vigorosa e umidade compatível com boa disponibilidade floral."
    elif ndvi >= 0.45 and ndwi >= -0.05:
        status = "atenção"
        risk = "moderado"
        message = "Vegetação ainda funcional, mas com sinais de redução de vigor ou água."
    else:
        status = "risco"
        risk = "alto"
        message = "Baixo vigor vegetal pode indicar queda de florada ou estresse hídrico."

    return {"vegetation_status": status, "vegetation_risk": risk, "vegetation_message": message}


def compare_environmental_variation(current: pd.Series | dict, previous: pd.Series | dict) -> dict[str, float]:
    """Compare microenvironmental and Copernicus indicators between two dates."""

    current = pd.Series(current, dtype="float64")
    previous = pd.Series(previous, dtype="float64")
    shared = [col for col in current.index if col in previous.index]
    return {f"delta_{col}": float(current[col] - previous[col]) for col in shared}


def calculate_bee_environmental_health_score(row: pd.Series | dict) -> float:
    """Experimental Bee Environmental Health Score from 0 to 100.

    The score blends macro indicators (NDVI/NDWI), local climate, productivity,
    acoustic stability and bee activity. It is transparent by design for hackathon
    explainability, not a clinical diagnosis of hive health.
    """

    row = pd.Series(row)

    def value(name: str, default: float) -> float:
        return float(pd.to_numeric(row.get(name, default), errors="coerce"))

    ndvi_score = np.interp(value("ndvi", 0.5), [0.2, 0.75], [0, 100])
    ndwi_score = np.interp(value("ndwi", 0.0), [-0.25, 0.35], [0, 100])
    temp_score = 100 - abs(value("temperature_c", 30.0) - 32.5) * 8
    humidity_score = 100 - abs(value("humidity_pct", 58.0) - 58.0) * 2.2
    productivity_score = np.interp(value("weight_delta_kg_7d", 0.4), [-3.0, 2.5], [0, 100])
    activity_score = np.interp(value("bee_activity", 0.72), [0.25, 1.0], [0, 100])
    acoustic_score = 100 * (1 - np.clip(value("acoustic_anomaly", 0.15), 0, 1))

    score = (
        0.28 * ndvi_score
        + 0.12 * ndwi_score
        + 0.16 * temp_score
        + 0.12 * humidity_score
        + 0.14 * productivity_score
        + 0.10 * activity_score
        + 0.08 * acoustic_score
    )
    return round(float(np.clip(score, 0, 100)), 1)


def score_label(score: float) -> str:
    if score >= 80:
        return "ambiente saudável"
    if score >= 50:
        return "atenção"
    return "risco ambiental"


def generate_environmental_alerts(row: pd.Series | dict, thresholds: EnvironmentalThresholds | None = None) -> list[dict[str, str]]:
    """Generate threshold-based alerts for the dashboard."""

    thresholds = thresholds or EnvironmentalThresholds()
    row = pd.Series(row)
    alerts: list[dict[str, str]] = []

    if float(row.get("ndvi_delta_14d", 0)) <= thresholds.ndvi_drop_alert:
        alerts.append({
            "severity": "alta",
            "title": "Possível redução de florada",
            "detail": "Queda brusca de NDVI no buffer de voo de 3 km da colmeia.",
        })
    if float(row.get("ndvi", 1)) < thresholds.ndvi_low:
        alerts.append({
            "severity": "média",
            "title": "Possível estresse ambiental",
            "detail": "NDVI baixo sugere menor vigor vegetal no microambiente monitorado.",
        })
    if float(row.get("temperature_c", 0)) >= thresholds.temperature_high_c:
        alerts.append({
            "severity": "alta",
            "title": "Possível impacto climático",
            "detail": "Temperatura acima do limiar operacional para conforto térmico da colmeia.",
        })
    if float(row.get("humidity_pct", 100)) <= thresholds.humidity_low_pct:
        alerts.append({
            "severity": "média",
            "title": "Possível estresse ambiental",
            "detail": "Baixa umidade interna pode intensificar risco de desidratação e perda de produtividade.",
        })
    if float(row.get("acoustic_anomaly", 0)) >= thresholds.acoustic_anomaly_high:
        alerts.append({
            "severity": "alta",
            "title": "Anomalia de sensores",
            "detail": "Assinatura acústica anômala detectada; recomenda-se inspeção preventiva.",
        })
    if float(row.get("weight_delta_kg_7d", 0)) <= thresholds.weight_loss_kg_7d:
        alerts.append({
            "severity": "alta",
            "title": "Possível redução de florada",
            "detail": "Perda de peso em 7 dias pode indicar menor entrada de néctar ou estresse da colônia.",
        })

    if not alerts:
        alerts.append({
            "severity": "baixa",
            "title": "Colmeia em observação normal",
            "detail": "Nenhum threshold crítico foi ultrapassado no último ciclo de análise.",
        })
    return alerts


def add_scores_and_alerts(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach score, class and compact alert count to a dataframe."""

    enriched = frame.copy()
    enriched["bee_environmental_health_score"] = enriched.apply(calculate_bee_environmental_health_score, axis=1)
    enriched["score_status"] = enriched["bee_environmental_health_score"].map(score_label)
    enriched["alert_count"] = enriched.apply(lambda row: sum(alert["severity"] != "baixa" for alert in generate_environmental_alerts(row)), axis=1)
    return enriched


def summarize_alert_titles(alerts: Iterable[dict[str, str]]) -> str:
    return " · ".join(alert["title"] for alert in alerts)
