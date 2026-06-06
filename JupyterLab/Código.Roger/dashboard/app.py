"""Streamlit dashboard for BeeSpace CopernicusLAC Panamá 2026 MVP."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from analytics.environment import analyze_vegetation_health, generate_environmental_alerts
from copernicus.sentinel_hub import HiveLocation, get_ndvi
from iot.simulator import simulate_hive_timeseries
from mock_data.generate_demo_data import build_demo_dataset
from vision.yolo_pipeline import mock_honeycomb_inference

OUTPUT_DIR = PROJECT_DIR / "outputs"


@st.cache_data(show_spinner=False)
def load_timeseries() -> pd.DataFrame:
    csv_path = OUTPUT_DIR / "beespace_demo_timeseries.csv"
    if not csv_path.exists():
        build_demo_dataset(OUTPUT_DIR)
    return pd.read_csv(csv_path, parse_dates=["timestamp"])


@st.cache_data(show_spinner=False)
def load_ndvi_raster() -> np.ndarray:
    location = HiveLocation("BS-PAN-001", latitude=8.9824, longitude=-79.5199)
    result = get_ndvi(location, prefer_real_api=False, output_dir=OUTPUT_DIR)
    return result["raster"]


def metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label=label, value=value, help=help_text)


def render_header() -> None:
    st.set_page_config(page_title="BeeSpace ClimateTech MVP", page_icon="🐝", layout="wide")
    st.markdown(
        """
        <style>
        .main {background: linear-gradient(180deg, #071312 0%, #101820 100%);}
        div[data-testid="stMetric"] {background: #13231f; border: 1px solid #2f6f54; padding: 14px; border-radius: 18px;}
        .alert-box {padding: 14px; border-radius: 14px; margin-bottom: 10px; background: #291b12; border: 1px solid #ffb000;}
        .bee-title {font-size: 2.6rem; font-weight: 800; color: #ffcc33; margin-bottom: 0;}
        .bee-subtitle {font-size: 1.05rem; color: #d8f3dc; margin-top: 0;}
        </style>
        <p class="bee-title">🐝 BeeSpace · Biodiversidade em Órbita</p>
        <p class="bee-subtitle">Colmeias IoT + Copernicus Sentinel-2 + Bioacústica + ESG para resiliência de pequenos agricultores.</p>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    render_header()
    data = load_timeseries()
    latest = data.iloc[-1]
    previous = data.iloc[-15]
    location = HiveLocation(latest.hive_id, latest.latitude, latest.longitude)
    alerts = generate_environmental_alerts(latest)
    vegetation = analyze_vegetation_health(float(latest.ndvi), float(latest.ndwi))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Bee Environmental Health Score", f"{latest.bee_environmental_health_score:.1f}/100", "80-100 saudável · 50-79 atenção · 0-49 risco")
    with col2:
        metric_card("Status da colmeia", str(latest.score_status).title())
    with col3:
        metric_card("Área monitorada", f"{location.monitored_area_hectares:,.0f} ha".replace(",", "."), "Raio de voo de 3 km")
    with col4:
        metric_card("Alertas ativos", str(sum(a["severity"] != "baixa" for a in alerts)))

    st.divider()
    left, right = st.columns([1.1, 0.9])
    with left:
        fig_map = px.scatter_mapbox(
            pd.DataFrame([latest]),
            lat="latitude",
            lon="longitude",
            hover_name="hive_id",
            hover_data={"bee_environmental_health_score": True, "ndvi": True, "humidity_pct": True},
            zoom=10,
            height=470,
            color=[latest.bee_environmental_health_score],
            color_continuous_scale="RdYlGn",
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=30, b=0), title="Mapa da colmeia e microambiente monitorado")
        st.plotly_chart(fig_map, use_container_width=True)
    with right:
        raster = load_ndvi_raster()
        fig_ndvi = px.imshow(raster, color_continuous_scale="RdYlGn", zmin=0.15, zmax=0.9, title="NDVI Sentinel-2 no buffer de 3 km")
        fig_ndvi.update_layout(height=470, coloraxis_colorbar_title="NDVI", margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig_ndvi, use_container_width=True)

    st.subheader("🚨 Alertas ambientais automáticos")
    for alert in alerts:
        icon = "🔴" if alert["severity"] == "alta" else "🟠" if alert["severity"] == "média" else "🟢"
        st.markdown(f"<div class='alert-box'><b>{icon} {alert['title']}</b><br>{alert['detail']}</div>", unsafe_allow_html=True)

    st.subheader("📈 Pipeline ingestão → processamento → visualização")
    c1, c2 = st.columns(2)
    with c1:
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=data.timestamp, y=data.ndvi, name="Micro NDVI colmeia", line=dict(color="#59d65f", width=3)))
        fig_ts.add_trace(go.Scatter(x=data.timestamp, y=data.macro_ndvi, name="Macro NDVI Copernicus", line=dict(color="#7cc7ff", dash="dash")))
        fig_ts.add_trace(go.Bar(x=data.timestamp, y=data.precipitation_mm / 20, name="Chuva reescalada", marker_color="rgba(88,166,255,0.35)"))
        fig_ts.update_layout(title="Timeline ambiental: microambiente vs macroambiente", yaxis_title="Índice", height=390)
        st.plotly_chart(fig_ts, use_container_width=True)
    with c2:
        fig_climate = px.line(
            data,
            x="timestamp",
            y=["temperature_c", "humidity_pct"],
            title="Sensores climáticos internos da colmeia",
            height=390,
        )
        st.plotly_chart(fig_climate, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_score = px.area(data, x="timestamp", y="bee_environmental_health_score", title="Bee Environmental Health Score", color_discrete_sequence=["#ffcc33"])
        fig_score.add_hrect(y0=80, y1=100, fillcolor="green", opacity=0.12, line_width=0)
        fig_score.add_hrect(y0=50, y1=80, fillcolor="orange", opacity=0.12, line_width=0)
        fig_score.add_hrect(y0=0, y1=50, fillcolor="red", opacity=0.12, line_width=0)
        st.plotly_chart(fig_score, use_container_width=True)
    with c4:
        vision = mock_honeycomb_inference()
        fig_vision = px.pie(vision, names="class_name", values="percent_area", title="Visão computacional do favo (mock YOLO-ready)", hole=0.45)
        st.plotly_chart(fig_vision, use_container_width=True)

    st.subheader("🌱 Cards ESG e biodiversidade")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Vigor vegetal", vegetation["vegetation_status"].title(), vegetation["vegetation_risk"])
    e2.metric("NDVI 14 dias", f"{latest.ndvi_delta_14d:+.3f}", "queda indica risco de florada")
    e3.metric("Peso 7 dias", f"{latest.weight_delta_kg_7d:+.2f} kg", "proxy de produtividade")
    e4.metric("Gap micro/macro", f"{latest.macro_micro_ndvi_gap:+.3f}", "colmeia vs Copernicus regional")

    with st.expander("🔬 Detalhes técnicos do MVP"):
        st.write(
            {
                "pipeline": "IoT simulator → Copernicus Sentinel Hub wrapper → analytics thresholds → Streamlit dashboard",
                "sentinel_hub_mode": "usa SENTINELHUB_CLIENT_ID/SECRET quando disponíveis; fallback sintético determinístico para demo",
                "previous_ndvi": float(previous.ndvi),
                "current_ndvi": float(latest.ndvi),
                "vegetation_message": vegetation["vegetation_message"],
            }
        )


if __name__ == "__main__":
    render_dashboard()
