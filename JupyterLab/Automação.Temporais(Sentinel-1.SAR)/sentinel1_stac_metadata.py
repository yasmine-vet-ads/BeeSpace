"""
BeeSpace | Consulta automática de metadados Sentinel-1 SAR via STAC

Script preparado para execução em JupyterLab ou terminal. Ele consulta metadados
Sentinel-1 GRD (modo IW) dos últimos 30 dias em uma área simulada na Serra
Gaúcha, sem baixar rasters ou assets pesados.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import geopandas as gpd
import pandas as pd
from pystac_client import Client
from pystac_client.exceptions import APIError
from pystac_client.stac_api_io import StacApiIO
from shapely.geometry import box

try:
    from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, Timeout
except ImportError:  # pragma: no cover - requests é dependência transitiva comum do pystac-client.
    ConnectionError = HTTPError = ReadTimeout = Timeout = OSError  # type: ignore[misc,assignment]


# -----------------------------------------------------------------------------
# Configurações da área de interesse e da janela temporal
# -----------------------------------------------------------------------------

# Bounding box simulada para uma área florestal na Serra Gaúcha / RS / Brasil.
# Formato: [min_lon, min_lat, max_lon, max_lat]
BBOX_SERRA_GAUCHA = [-51.25, -29.35, -50.65, -28.85]

STAC_API_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION_ID = "sentinel-1-grd"
LOOKBACK_DAYS = 30
API_TIMEOUT_SECONDS = 30


def build_area_of_interest(bbox: list[float]) -> gpd.GeoDataFrame:
    """Cria um GeoDataFrame da área de interesse a partir de uma bounding box."""
    geometry = [box(*bbox)]
    return gpd.GeoDataFrame(
        {"nome": ["Serra Gaúcha - área simulada BeeSpace"]},
        geometry=geometry,
        crs="EPSG:4326",
    )


def build_datetime_interval(days: int = LOOKBACK_DAYS) -> str:
    """Retorna o intervalo temporal STAC no padrão ISO-8601 para os últimos N dias."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    return f"{start_date.isoformat()}/{end_date.isoformat()}"


def normalize_polarizations(value: Any) -> str:
    """Normaliza a lista de polarizações SAR para uma string legível."""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item).upper() for item in value)
    if value:
        return str(value).upper()
    return "Não informado"


def search_sentinel1_metadata(
    bbox: list[float],
    datetime_interval: str,
    limit: int = 100,
) -> pd.DataFrame:
    """
    Consulta cenas Sentinel-1 GRD no modo IW e devolve os metadados essenciais.

    A função evita download de arquivos raster; somente os documentos STAC dos
    itens encontrados são lidos para compor o DataFrame final.
    """
    stac_io = StacApiIO(max_retries=3, timeout=API_TIMEOUT_SECONDS)

    try:
        catalog = Client.open(STAC_API_URL, stac_io=stac_io)
        search = catalog.search(
            collections=[COLLECTION_ID],
            bbox=bbox,
            datetime=datetime_interval,
            limit=limit,
            query={"sar:instrument_mode": {"eq": "IW"}},
        )
        items = list(search.items())

    except (APIError, ConnectionError, HTTPError, ReadTimeout, Timeout) as exc:
        print("⚠️ Falha ao consultar a API STAC do Earth Search.")
        print(f"Detalhes técnicos: {type(exc).__name__}: {exc}")
        return pd.DataFrame(
            columns=[
                "Data_Aquisicao",
                "ID_Cena",
                "Orbita",
                "Polarizacoes_Disponiveis",
            ]
        )
    except Exception as exc:  # Proteção adicional para notebooks operacionais.
        print("⚠️ Erro inesperado durante a consulta de metadados Sentinel-1.")
        print(f"Detalhes técnicos: {type(exc).__name__}: {exc}")
        return pd.DataFrame(
            columns=[
                "Data_Aquisicao",
                "ID_Cena",
                "Orbita",
                "Polarizacoes_Disponiveis",
            ]
        )

    records: list[dict[str, str]] = []
    for item in items:
        properties = item.properties
        records.append(
            {
                "Data_Aquisicao": properties.get("datetime", item.datetime.isoformat() if item.datetime else "Não informado"),
                "ID_Cena": item.id,
                "Orbita": str(properties.get("sat:orbit_state", "Não informado")).title(),
                "Polarizacoes_Disponiveis": normalize_polarizations(
                    properties.get("sar:polarizations")
                ),
            }
        )

    dataframe = pd.DataFrame.from_records(
        records,
        columns=[
            "Data_Aquisicao",
            "ID_Cena",
            "Orbita",
            "Polarizacoes_Disponiveis",
        ],
    )

    if not dataframe.empty:
        dataframe = dataframe.sort_values("Data_Aquisicao", ascending=False).reset_index(drop=True)

    return dataframe


def main() -> pd.DataFrame:
    """Executa a consulta e imprime o DataFrame final formatado."""
    area_of_interest = build_area_of_interest(BBOX_SERRA_GAUCHA)
    datetime_interval = build_datetime_interval()

    print("🛰️ BeeSpace | Consulta Sentinel-1 GRD via STAC")
    print(f"Área de interesse: {area_of_interest.loc[0, 'nome']}")
    print(f"Bounding Box: {BBOX_SERRA_GAUCHA}")
    print(f"Janela temporal: {datetime_interval}")
    print("Filtro SAR: modo de aquisição IW (Interferometric Wide swath)\n")

    dataframe = search_sentinel1_metadata(BBOX_SERRA_GAUCHA, datetime_interval)

    if dataframe.empty:
        print("Nenhuma cena Sentinel-1 GRD/IW encontrada para os filtros informados.")
    else:
        print(dataframe.to_string(index=False))

    return dataframe


if __name__ == "__main__":
    df_sentinel1 = main()
