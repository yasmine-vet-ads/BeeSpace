<div align="center">

# 🐝 BeeSpace · MVP ClimateTech CopernicusLAC Panamá 2026

**Colmeias como biossensores vivos conectados ao Copernicus para apoiar a resiliência de pequenos agricultores.**

![Copernicus](https://img.shields.io/badge/Copernicus-Sentinel--2-0B3D91?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=for-the-badge)
![IoT](https://img.shields.io/badge/IoT-Telemetria-FFB000?style=for-the-badge)
![ClimateTech](https://img.shields.io/badge/ClimateTech-Biodiversidade-2E7D32?style=for-the-badge)

</div>

---

## 🎯 Objetivo do MVP

Este diretório transforma a trilha de notebooks BeeSpace em um **MVP executável e visualmente forte** para hackathon. A proposta demonstra, de ponta a ponta, como uma colmeia georreferenciada pode integrar:

- sensores IoT embarcados;
- telemetria sintética realista para demonstração;
- consulta modular ao Sentinel Hub API;
- NDVI/NDWI no raio de voo de 3 km;
- comparação entre microambiente da colmeia e macroambiente Copernicus;
- alertas ambientais automáticos;
- Bee Environmental Health Score de 0 a 100;
- dashboard científico em Streamlit;
- pipeline preparado para visão computacional com YOLO.

> O foco é um MVP plausível, estável e demo-ready, não uma plataforma enterprise.

---

## 🧭 Arquitetura implementada

```text
JupyterLab/Código.Roger/
├── api/                  # Contratos mínimos para futura ingestão de telemetria
├── analytics/            # Scores, thresholds, alertas e comparação temporal
├── copernicus/           # Wrapper Sentinel Hub + fallback sintético determinístico
├── dashboard/            # Dashboard Streamlit para apresentação ao vivo
├── iot/                  # Simulador realista de telemetria de colmeia
├── mock_data/            # Geração de datasets e artefatos de demo
├── notebooks/            # Documentação para notebooks derivados
├── outputs/              # CSVs, metadados e rasters gerados localmente
├── vision/               # Scaffold YOLO-ready para análise de favos
├── requirements.txt
└── README.md
```

---

## 🛰️ Pipeline Copernicus

O módulo `copernicus/sentinel_hub.py` expõe funções reutilizáveis:

```python
from copernicus.sentinel_hub import HiveLocation, get_ndvi, get_ndwi

hive = HiveLocation("BS-PAN-001", latitude=8.9824, longitude=-79.5199)
ndvi = get_ndvi(hive, start_date="2026-05-01", end_date="2026-06-01")
ndwi = get_ndwi(hive, start_date="2026-05-01", end_date="2026-06-01")
```

### Modos de execução

| Modo | Como funciona | Uso no hackathon |
|---|---|---|
| **Real Sentinel Hub** | Usa `SENTINELHUB_CLIENT_ID` e `SENTINELHUB_CLIENT_SECRET` para chamar a Process API. | Demonstra integração real com Copernicus/Sentinel-2 quando houver credenciais. |
| **Fallback sintético** | Gera rasters NDVI/NDWI determinísticos e realistas quando não há credenciais. | Garante demo estável mesmo sem internet, sem conta ou sem quota. |

O buffer da colmeia usa raio de voo de **3 km**, equivalente a aproximadamente **2.827 hectares monitorados**.

---

## 🌡️ Sistema de alertas ambientais

O arquivo `analytics/environment.py` implementa thresholds simples e explicáveis:

- queda brusca de NDVI em 14 dias;
- NDVI abaixo do limiar de vigor vegetal;
- temperatura interna elevada;
- baixa umidade interna;
- anomalia acústica;
- perda de peso em 7 dias.

Alertas gerados automaticamente:

- **Possível estresse ambiental**;
- **Possível redução de florada**;
- **Possível impacto climático**;
- **Anomalia de sensores**.

---

## 🧮 Bee Environmental Health Score

O score experimental combina variáveis macroambientais e sinais da colmeia:

| Variável | Papel |
|---|---|
| NDVI | vigor da vegetação e potencial de florada |
| NDWI | disponibilidade hídrica da vegetação |
| Temperatura | conforto térmico interno |
| Umidade | estabilidade do microclima da colmeia |
| Variação de peso | proxy de produtividade/entrada de néctar |
| Atividade das abelhas | intensidade operacional da colônia |
| Anomalia acústica | estabilidade bioacústica |

Interpretação:

| Score | Classe |
|---:|---|
| 80–100 | ambiente saudável |
| 50–79 | atenção |
| 0–49 | risco ambiental |

---

## 🖥️ Dashboard científico

O dashboard Streamlit foi desenhado para impressionar visualmente os avaliadores e mostrar o pipeline completo:

- mapa da colmeia no Panamá;
- área monitorada de 2.827 hectares;
- mapa raster de NDVI;
- timeline ambiental;
- série temporal de temperatura e umidade;
- Bee Environmental Health Score;
- alertas automáticos;
- cards ESG;
- comparação microambiente da colmeia vs macroambiente Copernicus;
- gráfico percentual do favo preparado para YOLO.

---

## 🚀 Como executar

### 1. Instalar dependências

```bash
cd JupyterLab/Código.Roger
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Gerar dados e artefatos da demo

```bash
python mock_data/generate_demo_data.py
```

Saídas principais em `outputs/`:

- `beespace_demo_timeseries.csv`;
- `beespace_latest_snapshot.csv`;
- `honeycomb_mock_inference.csv`;
- arquivos `.npy` e `.json` de NDVI/NDWI.

### 3. Abrir o dashboard

```bash
streamlit run dashboard/app.py
```

### 4. Opcional: usar Sentinel Hub real

```bash
export SENTINELHUB_CLIENT_ID="seu-client-id"
export SENTINELHUB_CLIENT_SECRET="seu-client-secret"
python mock_data/generate_demo_data.py
```

Se a API falhar ou as credenciais não estiverem configuradas, o MVP usa fallback sintético para preservar a apresentação ao vivo.

---

## 🧪 Exemplo de pipeline em Python

```python
from analytics.environment import add_scores_and_alerts, generate_environmental_alerts
from copernicus.sentinel_hub import HiveLocation, get_ndvi, get_ndwi
from iot.simulator import simulate_hive_timeseries

telemetry = simulate_hive_timeseries()
telemetry = add_scores_and_alerts(telemetry)

hive = HiveLocation("BS-PAN-001", 8.9824, -79.5199)
ndvi = get_ndvi(hive, prefer_real_api=False)
ndwi = get_ndwi(hive, prefer_real_api=False)

latest = telemetry.iloc[-1]
alerts = generate_environmental_alerts(latest)
print(latest["bee_environmental_health_score"], alerts)
```

---

## 🧠 Visão computacional YOLO-ready

O arquivo `vision/yolo_pipeline.py` organiza diretórios e gera uma inferência mockada plausível para análise de favo. Em uma evolução real, basta substituir `mock_honeycomb_inference()` por uma chamada a YOLOv8/YOLOv11 treinado com classes como mel operculado, néctar, ovos/larvas, pupas, células vazias e anomalias.

---

## 🌎 Mensagem para os jurados

A BeeSpace mostra que uma colmeia não é apenas uma unidade produtiva: ela pode se tornar um **sensor vivo territorial**. Ao cruzar Copernicus, IoT e IA, pequenos agricultores ganham alertas acionáveis sobre florada, estresse hídrico, produtividade e biodiversidade — com uma arquitetura simples o suficiente para um hackathon e escalável o suficiente para um produto ClimateTech real.
