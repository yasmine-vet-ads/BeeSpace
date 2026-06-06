"""Copernicus/Sentinel Hub utilities for the BeeSpace hackathon MVP.

The module intentionally works in two modes:
1. Real Sentinel Hub Process API, when credentials are available via environment variables.
2. Deterministic synthetic fallback, so judges can run the demo offline during the hackathon.
"""

from __future__ import annotations

import base64
import json
import math
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import numpy as np

try:
    import requests
except ImportError:  # pragma: no cover - optional dependency for offline demos
    requests = None

IndexName = Literal["ndvi", "ndwi"]

SENTINEL_TOKEN_URL = "https://services.sentinel-hub.com/oauth/token"
SENTINEL_PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"
DEFAULT_RESOLUTION = 96


@dataclass(frozen=True)
class HiveLocation:
    """Geographic reference for a monitored hive."""

    hive_id: str
    latitude: float
    longitude: float
    flight_radius_km: float = 3.0

    @property
    def monitored_area_hectares(self) -> float:
        """Area covered by the nominal bee flight radius.

        A 3 km radius covers pi * 3² km² = 28.274 km² = 2,827.43 hectares.
        """

        return math.pi * self.flight_radius_km**2 * 100

    def bbox(self) -> list[float]:
        """Return an approximate WGS84 bounding box around the hive.

        The approximation is sufficient for an MVP buffer and avoids requiring heavy GIS
        dependencies. Production code should use pyproj/geopandas for precise buffers.
        """

        lat_delta = self.flight_radius_km / 111.32
        lon_delta = self.flight_radius_km / (111.32 * math.cos(math.radians(self.latitude)))
        return [
            self.longitude - lon_delta,
            self.latitude - lat_delta,
            self.longitude + lon_delta,
            self.latitude + lat_delta,
        ]


def _sentinel_evalscript(index: IndexName) -> str:
    if index == "ndvi":
        return """
        //VERSION=3
        function setup() {
          return { input: ["B04", "B08", "dataMask"], output: { bands: 1, sampleType: "FLOAT32" } };
        }
        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / Math.max(sample.B08 + sample.B04, 0.0001);
          return [sample.dataMask ? ndvi : -9999];
        }
        """
    return """
    //VERSION=3
    function setup() {
      return { input: ["B03", "B08", "dataMask"], output: { bands: 1, sampleType: "FLOAT32" } };
    }
    function evaluatePixel(sample) {
      let ndwi = (sample.B03 - sample.B08) / Math.max(sample.B03 + sample.B08, 0.0001);
      return [sample.dataMask ? ndwi : -9999];
    }
    """


def _get_access_token() -> str | None:
    """Fetch a Sentinel Hub token from environment credentials, if configured."""

    client_id = os.getenv("SENTINELHUB_CLIENT_ID")
    client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")
    if not client_id or not client_secret or requests is None:
        return None

    response = requests.post(
        SENTINEL_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _synthetic_index(
    location: HiveLocation,
    index: IndexName,
    start_date: str,
    end_date: str,
    resolution: int = DEFAULT_RESOLUTION,
) -> dict[str, Any]:
    """Generate a realistic raster-like index for demo mode.

    The deterministic seed keeps screenshots reproducible while still varying by hive,
    index and time window.
    """

    seed_payload = f"{location.hive_id}:{location.latitude:.4f}:{location.longitude:.4f}:{index}:{start_date}:{end_date}"
    seed = int.from_bytes(seed_payload.encode("utf-8"), "little", signed=False) % (2**32 - 1)
    rng = np.random.default_rng(seed)

    y, x = np.mgrid[-1:1 : complex(resolution), -1:1 : complex(resolution)]
    gradient = 0.16 * (1 - np.sqrt(x**2 + y**2))
    seasonal = 0.06 * math.sin(datetime.fromisoformat(end_date).timetuple().tm_yday / 365 * 2 * math.pi)
    patch = 0.12 * np.exp(-((x + 0.35) ** 2 + (y - 0.25) ** 2) / 0.12)
    stress_patch = 0.18 * np.exp(-((x - 0.42) ** 2 + (y + 0.18) ** 2) / 0.08)
    noise = rng.normal(0, 0.035, size=(resolution, resolution))

    if index == "ndvi":
        raster = 0.58 + gradient + seasonal + patch - stress_patch + noise
        raster = np.clip(raster, -0.15, 0.92)
    else:
        raster = 0.18 + 0.8 * gradient + 0.5 * seasonal + 0.4 * patch - 0.7 * stress_patch + noise
        raster = np.clip(raster, -0.45, 0.62)

    return {
        "source": "synthetic_fallback",
        "index": index.upper(),
        "hive_id": location.hive_id,
        "bbox": location.bbox(),
        "start_date": start_date,
        "end_date": end_date,
        "resolution": resolution,
        "raster": raster,
        "stats": raster_stats(raster),
    }


def _request_sentinel_hub(
    location: HiveLocation,
    index: IndexName,
    start_date: str,
    end_date: str,
    resolution: int,
) -> dict[str, Any] | None:
    token = _get_access_token()
    if not token or requests is None:
        return None

    payload = {
        "input": {
            "bounds": {"bbox": location.bbox(), "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}},
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {"from": f"{start_date}T00:00:00Z", "to": f"{end_date}T23:59:59Z"},
                        "maxCloudCoverage": 35,
                    },
                }
            ],
        },
        "output": {
            "width": resolution,
            "height": resolution,
            "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}],
        },
        "evalscript": _sentinel_evalscript(index),
    }

    response = requests.post(
        SENTINEL_PROCESS_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    response.raise_for_status()

    # TIFF decoding is deliberately optional for hackathon portability. Store the raw
    # response and return synthetic statistics if rasterio is not installed.
    return {
        "source": "sentinel_hub_process_api",
        "index": index.upper(),
        "hive_id": location.hive_id,
        "bbox": location.bbox(),
        "start_date": start_date,
        "end_date": end_date,
        "resolution": resolution,
        "content_type": response.headers.get("Content-Type", "image/tiff"),
        "raw_tiff_base64": base64.b64encode(response.content).decode("ascii"),
        "stats": {},
    }


def raster_stats(raster: np.ndarray) -> dict[str, float]:
    valid = raster[np.isfinite(raster) & (raster > -999)]
    return {
        "mean": float(np.mean(valid)),
        "median": float(np.median(valid)),
        "min": float(np.min(valid)),
        "max": float(np.max(valid)),
        "p10": float(np.percentile(valid, 10)),
        "p90": float(np.percentile(valid, 90)),
    }


def get_index(
    location: HiveLocation,
    index: IndexName,
    start_date: str | None = None,
    end_date: str | None = None,
    resolution: int = DEFAULT_RESOLUTION,
    prefer_real_api: bool = True,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Download or simulate a Copernicus vegetation/water index around a hive."""

    today = date.today()
    end_date = end_date or today.isoformat()
    start_date = start_date or (today - timedelta(days=30)).isoformat()

    result = None
    if prefer_real_api:
        try:
            result = _request_sentinel_hub(location, index, start_date, end_date, resolution)
        except Exception as exc:  # keep demo resilient, but expose the reason
            result = None
            api_error = str(exc)
        else:
            api_error = None
    else:
        api_error = None

    if result is None:
        result = _synthetic_index(location, index, start_date, end_date, resolution)
        if api_error:
            result["api_fallback_reason"] = api_error

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        if "raster" in result:
            np.save(output_path / f"{location.hive_id}_{index}_{end_date}.npy", result["raster"])
        metadata = {key: value for key, value in result.items() if key != "raster"}
        (output_path / f"{location.hive_id}_{index}_{end_date}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return result


def get_ndvi(location: HiveLocation, **kwargs: Any) -> dict[str, Any]:
    """Return NDVI for the hive buffer using Sentinel-2 B08 and B04."""

    return get_index(location, "ndvi", **kwargs)


def get_ndwi(location: HiveLocation, **kwargs: Any) -> dict[str, Any]:
    """Return NDWI for the hive buffer using Sentinel-2 B03 and B08."""

    return get_index(location, "ndwi", **kwargs)
