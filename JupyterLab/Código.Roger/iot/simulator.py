"""Realistic IoT telemetry simulator for BeeSpace live demos."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def simulate_hive_timeseries(
    hive_id: str = "BS-PAN-001",
    periods: int = 60,
    freq: str = "D",
    start: str | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Create realistic synthetic telemetry for a connected hive.

    Variables include internal temperature, humidity, weight, acoustic anomaly,
    bee activity and macro Copernicus indicators. The final days include a mild
    stress episode so the dashboard has meaningful alerts for presentation.
    """

    rng = np.random.default_rng(seed)
    start_dt = pd.Timestamp(start or (datetime.utcnow() - timedelta(days=periods - 1)).date())
    timestamps = pd.date_range(start=start_dt, periods=periods, freq=freq)
    day = np.arange(periods)

    seasonal = np.sin(np.linspace(0, 2.4 * np.pi, periods))
    stress = np.zeros(periods)
    stress[-14:] = np.linspace(0, 1, 14)

    temperature_c = 31.2 + 2.0 * seasonal + 4.2 * stress + rng.normal(0, 0.55, periods)
    humidity_pct = 60.0 - 10.5 * stress - 3.0 * seasonal + rng.normal(0, 1.4, periods)
    hive_weight_kg = 36 + np.cumsum(rng.normal(0.11, 0.16, periods)) - 2.6 * stress
    bee_activity = np.clip(0.78 + 0.08 * seasonal - 0.23 * stress + rng.normal(0, 0.035, periods), 0.2, 1.0)
    acoustic_anomaly = np.clip(0.12 + 0.50 * stress + rng.normal(0, 0.045, periods), 0, 1)
    ndvi = np.clip(0.66 - 0.18 * stress + 0.04 * seasonal + rng.normal(0, 0.018, periods), 0.15, 0.9)
    ndwi = np.clip(0.16 - 0.18 * stress + 0.03 * seasonal + rng.normal(0, 0.017, periods), -0.45, 0.65)
    macro_ndvi = np.clip(0.60 - 0.08 * stress + 0.03 * seasonal + rng.normal(0, 0.015, periods), 0.15, 0.9)
    precipitation_mm = np.clip(3.5 + 3.0 * rng.random(periods) - 3.0 * stress + rng.normal(0, 0.8, periods), 0, None)

    frame = pd.DataFrame(
        {
            "timestamp": timestamps,
            "hive_id": hive_id,
            "latitude": 8.9824,
            "longitude": -79.5199,
            "temperature_c": np.round(temperature_c, 2),
            "humidity_pct": np.round(humidity_pct, 2),
            "hive_weight_kg": np.round(hive_weight_kg, 2),
            "bee_activity": np.round(bee_activity, 3),
            "acoustic_anomaly": np.round(acoustic_anomaly, 3),
            "ndvi": np.round(ndvi, 3),
            "ndwi": np.round(ndwi, 3),
            "macro_ndvi": np.round(macro_ndvi, 3),
            "precipitation_mm": np.round(precipitation_mm, 2),
        }
    )
    frame["weight_delta_kg_7d"] = frame["hive_weight_kg"].diff(7).fillna(frame["hive_weight_kg"].diff().fillna(0)).round(2)
    frame["ndvi_delta_14d"] = frame["ndvi"].diff(14).fillna(frame["ndvi"].diff().fillna(0)).round(3)
    frame["macro_micro_ndvi_gap"] = (frame["ndvi"] - frame["macro_ndvi"]).round(3)
    frame["flight_radius_km"] = 3.0
    frame["monitored_area_hectares"] = 2827.43
    frame["foraging_area_label"] = "Raio de voo de 3 km · 2.827 hectares monitorados"
    return frame
