"""Computer vision scaffold prepared for YOLO honeycomb analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

HONEYCOMB_CLASSES = ["mel_operculado", "nectar", "ovos_larvas", "pupa", "celula_vazia", "anomalia"]


def create_vision_directories(base_dir: str | Path = "vision") -> dict[str, Path]:
    base = Path(base_dir)
    paths = {
        "images": base / "images",
        "labels": base / "labels",
        "runs": base / "runs",
        "models": base / "models",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def mock_honeycomb_inference(image_path: str | Path | None = None, seed: int = 7) -> pd.DataFrame:
    """Return a plausible class distribution as if a YOLO model had segmented a comb."""

    values = pd.Series(
        {
            "mel_operculado": 31.5,
            "nectar": 18.0,
            "ovos_larvas": 21.0,
            "pupa": 13.5,
            "celula_vazia": 12.0,
            "anomalia": 4.0,
        }
    )
    return pd.DataFrame(
        {
            "image_path": str(image_path or "demo_honeycomb.jpg"),
            "class_name": values.index,
            "percent_area": values.values,
            "interpretation": [
                "estoque de mel",
                "entrada recente de recurso floral",
                "cria aberta saudável",
                "desenvolvimento da colônia",
                "capacidade disponível",
                "ponto para inspeção manual",
            ],
        }
    )
