"""
BeeSpace - Módulo Geo-IoT
==========================

Script para JupyterLab/Copernicus que simula leituras de sensores IoT em
colmeias inteligentes, converte os dados em GeoDataFrame e renderiza um mapa
interativo com área de forrageamento e alertas ambientais.
"""

from __future__ import annotations

import html

import folium
import geopandas as gpd
import pandas as pd
from IPython.display import display
from shapely.geometry import Point


RAIO_FORRAGEAMENTO_M = 3_000
CRS_WGS84 = "EPSG:4326"


# -----------------------------------------------------------------------------
# 1) Dados tabulares simulados dos sensores IoT
#    Coordenadas realistas na região da Serra Gaúcha (RS, Brasil)
# -----------------------------------------------------------------------------
dados_sensores = [
    {
        "id_colmeia": "BS-SG-001",
        "latitude": -29.1678,
        "longitude": -51.1794,
        "temp_interna_c": 33.8,
        "umidade_perc": 58.4,
        "peso_kg": 42.7,
    },
    {
        "id_colmeia": "BS-SG-002",
        "latitude": -29.1906,
        "longitude": -51.2052,
        "temp_interna_c": 36.4,
        "umidade_perc": 44.2,
        "peso_kg": 39.5,
    },
    {
        "id_colmeia": "BS-SG-003",
        "latitude": -29.2521,
        "longitude": -51.5322,
        "temp_interna_c": 31.9,
        "umidade_perc": 37.6,
        "peso_kg": 47.9,
    },
    {
        "id_colmeia": "BS-SG-004",
        "latitude": -29.3585,
        "longitude": -51.5207,
        "temp_interna_c": 34.6,
        "umidade_perc": 62.1,
        "peso_kg": 51.3,
    },
    {
        "id_colmeia": "BS-SG-005",
        "latitude": -29.3042,
        "longitude": -51.3441,
        "temp_interna_c": 35.8,
        "umidade_perc": 39.1,
        "peso_kg": 44.8,
    },
]

df_colmeias = pd.DataFrame(dados_sensores)


# -----------------------------------------------------------------------------
# 2) Conversão para GeoDataFrame em EPSG:4326
# -----------------------------------------------------------------------------
gdf_colmeias = gpd.GeoDataFrame(
    df_colmeias,
    geometry=[Point(xy) for xy in zip(df_colmeias["longitude"], df_colmeias["latitude"])],
    crs=CRS_WGS84,
)


# -----------------------------------------------------------------------------
# 3) Mapa base Folium centralizado na média das coordenadas
# -----------------------------------------------------------------------------
centro_mapa = [gdf_colmeias.geometry.y.mean(), gdf_colmeias.geometry.x.mean()]

mapa_beespace = folium.Map(
    location=centro_mapa,
    zoom_start=10,
    tiles="CartoDB positron",
    control_scale=True,
)

camada_forrageamento = folium.FeatureGroup(
    name="Raio de Forrageamento (~3 km)",
    show=True,
)
camada_marcadores = folium.FeatureGroup(
    name="Marcadores IoT das Colmeias",
    show=True,
)


# -----------------------------------------------------------------------------
# 4) Camadas visuais: buffers de forrageamento e marcadores com alertas
# -----------------------------------------------------------------------------
for colmeia in gdf_colmeias.itertuples(index=False):
    em_alerta = colmeia.temp_interna_c > 35 or colmeia.umidade_perc < 40
    cor_status = "red" if em_alerta else "green"
    texto_status = "Alerta térmico/hídrico" if em_alerta else "Condição adequada"

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 220px;">
        <h4 style="margin: 0 0 8px; color: #6b3f00;">🐝 {html.escape(colmeia.id_colmeia)}</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr><td><strong>Status</strong></td><td style="color: {cor_status};">{texto_status}</td></tr>
            <tr><td><strong>Temp. interna</strong></td><td>{colmeia.temp_interna_c:.1f} °C</td></tr>
            <tr><td><strong>Umidade</strong></td><td>{colmeia.umidade_perc:.1f}%</td></tr>
            <tr><td><strong>Peso</strong></td><td>{colmeia.peso_kg:.1f} kg</td></tr>
            <tr><td><strong>Latitude</strong></td><td>{colmeia.latitude:.5f}</td></tr>
            <tr><td><strong>Longitude</strong></td><td>{colmeia.longitude:.5f}</td></tr>
        </table>
    </div>
    """

    coordenada = [colmeia.latitude, colmeia.longitude]

    folium.Circle(
        location=coordenada,
        radius=RAIO_FORRAGEAMENTO_M,
        color="#f59e0b",
        weight=2,
        fill=True,
        fill_color="#fbbf24",
        fill_opacity=0.18,
        popup=f"Área estimada de forrageamento: {RAIO_FORRAGEAMENTO_M / 1_000:.0f} km",
    ).add_to(camada_forrageamento)

    folium.Marker(
        location=coordenada,
        tooltip=f"{colmeia.id_colmeia} · {texto_status}",
        popup=folium.Popup(popup_html, max_width=320),
        icon=folium.Icon(color=cor_status, icon="info-sign"),
    ).add_to(camada_marcadores)


camada_forrageamento.add_to(mapa_beespace)
camada_marcadores.add_to(mapa_beespace)
folium.LayerControl(collapsed=False).add_to(mapa_beespace)


# Renderização direta no final da célula/notebook.
display(mapa_beespace)
