"""Minimal API contracts for future BeeSpace ingestion endpoints."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass(frozen=True)
class HiveTelemetryPayload:
    hive_id: str
    timestamp: str
    latitude: float
    longitude: float
    temperature_c: float
    humidity_pct: float
    hive_weight_kg: float
    bee_activity: float
    acoustic_anomaly: float

    @classmethod
    def demo(cls) -> "HiveTelemetryPayload":
        return cls(
            hive_id="BS-PAN-001",
            timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            latitude=8.9824,
            longitude=-79.5199,
            temperature_c=33.4,
            humidity_pct=54.2,
            hive_weight_kg=37.8,
            bee_activity=0.69,
            acoustic_anomaly=0.24,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
