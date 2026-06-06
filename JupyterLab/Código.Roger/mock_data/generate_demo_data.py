"""Generate all BeeSpace MVP demo artifacts in one command."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from analytics.environment import add_scores_and_alerts, generate_environmental_alerts, summarize_alert_titles
from copernicus.sentinel_hub import HiveLocation, get_ndvi, get_ndwi
from iot.simulator import simulate_hive_timeseries
from vision.yolo_pipeline import create_vision_directories, mock_honeycomb_inference


def build_demo_dataset(output_dir: str | Path | None = None) -> dict[str, Path]:
    output = Path(output_dir or PROJECT_DIR / "outputs")
    output.mkdir(parents=True, exist_ok=True)

    telemetry = add_scores_and_alerts(simulate_hive_timeseries())
    telemetry["alert_summary"] = telemetry.apply(lambda row: summarize_alert_titles(generate_environmental_alerts(row)), axis=1)
    telemetry_path = output / "beespace_demo_timeseries.csv"
    telemetry.to_csv(telemetry_path, index=False)

    location = HiveLocation("BS-PAN-001", latitude=float(telemetry.iloc[-1]["latitude"]), longitude=float(telemetry.iloc[-1]["longitude"]))
    ndvi = get_ndvi(location, prefer_real_api=False, output_dir=output)
    ndwi = get_ndwi(location, prefer_real_api=False, output_dir=output)

    latest = telemetry.iloc[-1].to_dict()
    latest.update(
        {
            "copernicus_ndvi_mean": ndvi["stats"]["mean"],
            "copernicus_ndwi_mean": ndwi["stats"]["mean"],
            "monitored_area_hectares": location.monitored_area_hectares,
        }
    )
    latest_path = output / "beespace_latest_snapshot.csv"
    pd.DataFrame([latest]).to_csv(latest_path, index=False)

    create_vision_directories(PROJECT_DIR / "vision")
    vision_path = output / "honeycomb_mock_inference.csv"
    mock_honeycomb_inference().to_csv(vision_path, index=False)

    return {"timeseries": telemetry_path, "latest_snapshot": latest_path, "vision": vision_path}


if __name__ == "__main__":
    artifacts = build_demo_dataset()
    for name, path in artifacts.items():
        print(f"{name}: {path}")
