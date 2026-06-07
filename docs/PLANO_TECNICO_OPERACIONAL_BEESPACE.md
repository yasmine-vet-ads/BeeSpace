# 📘 Plano Técnico Operacional BeeSpace

**Versão:** 1.0  
**Data:** 2026-06-07  
**Escopo:** guia executivo e operacional para evoluir a BeeSpace de MVP técnico para plataforma SaaS ClimateTech escalável, integrando colmeias instrumentadas, IoT rural, edge computing, Copernicus, IA, visão computacional, dashboard ESG, app mobile e marketplace apícola.

## Base analisada do repositório

Este plano parte da estrutura existente da BeeSpace:

- `README.md`: visão 360º com IoT embarcado, Copernicus, visão computacional, ML, MQTT e ESG.
- `firmware/`: firmware ESP32-S3 com PlatformIO, FreeRTOS, Arduino, sensores ambientais, áudio I2S, HX711, contadores, GPS, MOSFET, deep sleep e pipeline de IA separado em `IA.py`.
- `JupyterLab/Código.Roger/`: MVP científico com simulador IoT, wrapper Sentinel Hub, fallback sintético, dashboard Streamlit, analytics, notebooks e outputs NDVI/NDWI.
- `apps/mobile/`: app Expo/React Native inicial com telemetria, visão computacional e alertas ambientais mockados.
- `visao.computacional/`: pipeline YOLO/OpenCV para laudos quantitativos de favos.
- `MVP-BeeSpace/`: demo Streamlit/ML com imagens, dados sintéticos e modelo experimental.
- `SITE/`: site institucional e comunicação de produto.

---

# 1. Visão Geral da Arquitetura

## 1.1 Objetivo arquitetural

A BeeSpace deve ser uma plataforma modular que transforma colmeias em **estações autônomas de biovigilância ambiental**. Cada colmeia instrumentada coleta sinais internos e externos, processa parte dos dados na borda, envia telemetria resiliente para a nuvem e recebe enriquecimento com dados orbitais do Copernicus. A camada SaaS organiza usuários, fazendas, apiários, colmeias, sensores, modelos de IA, alertas, relatórios ESG, marketplace e APIs geoespaciais.

## 1.2 Arquitetura fim a fim

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                           TERRITÓRIO / APIÁRIO                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ Colmeia instrumentada                                                        │
│ ├─ ESP32-S3 / ESP32                                                          │
│ ├─ Sensores: temperatura, umidade, pressão, luz, peso, áudio, fluxo, bateria │
│ ├─ GPS/anti-furto, acelerômetro, storage local                               │
│ ├─ Energia: bateria LiFePO4/18650 + painel solar + BMS                       │
│ └─ Firmware: FreeRTOS, MQTT, deep sleep, buffer offline                       │
│                                                                              │
│ Gateway rural opcional                                                       │
│ ├─ Raspberry Pi / Jetson Nano / mini-PC                                      │
│ ├─ Broker MQTT local, cache, LoRa/Wi-Fi/4G                                   │
│ ├─ Edge AI leve: áudio, anomalia, compressão                                 │
│ └─ Sincronização com cloud quando houver internet                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ MQTT/TLS, HTTPS, LoRaWAN, 4G, Wi-Fi
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                               CLOUD BEESPACE                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ Ingestão IoT                                                                 │
│ ├─ MQTT broker gerenciado ou EMQX/Mosquitto                                  │
│ ├─ API FastAPI para ingestão HTTP fallback                                   │
│ ├─ Validação de payload, autenticação por dispositivo                        │
│ └─ Publicação de eventos em filas/streaming                                  │
│                                                                              │
│ Core SaaS                                                                    │
│ ├─ FastAPI REST/GraphQL opcional                                             │
│ ├─ PostgreSQL + PostGIS + TimescaleDB opcional                               │
│ ├─ Redis cache, rate limit e filas curtas                                    │
│ ├─ Celery/RQ/Arq para jobs assíncronos                                       │
│ ├─ WebSocket para alertas e dashboard em tempo real                          │
│ └─ Autenticação OAuth2/OIDC, JWT e RBAC                                      │
│                                                                              │
│ IA e dados                                                                   │
│ ├─ Pipelines ML: anomalias, séries temporais, scores e bioacústica           │
│ ├─ Visão computacional YOLO/OpenCV/Roboflow                                  │
│ ├─ MLOps: MLflow/DVC/model registry                                          │
│ ├─ ETL geoespacial Copernicus                                                │
│ └─ Data lake: imagens, rasters, modelos, logs                                │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              EXPERIÊNCIAS                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ App BeeSpace Monitor  │ Dashboard ESG │ Marketplace │ API geoespacial B2B/B2G │
│ Offline-first         │ Mapas/relatórios │ Produtos │ Dados ambientais         │
│ Alertas/push          │ KPIs ESG         │ Serviços │ Scores/alertas           │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 1.3 Relação entre hardware, backend, IA, Copernicus e apps

1. **Hardware IoT:** coleta sinais biológicos e ambientais da colmeia.
2. **Edge computing:** filtra ruído, calcula estatísticas locais, reduz consumo e preserva operação offline.
3. **Backend:** valida, persiste, processa e expõe dados via APIs.
4. **Copernicus:** fornece contexto territorial: vegetação, água, poluição, clima, uso do solo e risco ambiental.
5. **IA:** cruza sinais internos da colmeia com macroambiente para detectar anomalias, prever risco e classificar favos.
6. **Apps e dashboards:** transformam dados em ações de manejo, alertas, relatórios ESG e transações no marketplace.

## 1.4 Fluxo completo de dados

```text
[Sensores] -> [Firmware ESP32] -> [Payload JSON compacto]
    -> se internet: [MQTT/TLS cloud]
    -> se offline: [buffer flash/SD + retry]
    -> [validação contratual]
    -> [event bus]
    -> [PostgreSQL/PostGIS + séries temporais]
    -> [jobs assíncronos]
       ├─ normalização e agregação
       ├─ detecção de anomalias
       ├─ atualização de Bee Environmental Health Score
       ├─ consulta Copernicus por buffer de 3 km
       ├─ geração de alertas
       └─ notificação WebSocket/push/e-mail/WhatsApp
    -> [App Monitor + Dashboard ESG + API]
```

## 1.5 Arquitetura cloud

- **Entrada:** MQTT broker com TLS, API HTTP fallback e endpoint de upload de imagens.
- **Processamento:** workers assíncronos para telemetria, Copernicus, IA, relatórios e notificações.
- **Persistência:** PostgreSQL/PostGIS como banco principal; Redis para cache; S3 compatível para imagens, rasters e artefatos ML.
- **Entrega:** FastAPI, WebSocket, CDN, frontend web, app mobile e API pública versionada.
- **Observabilidade:** Prometheus, Grafana, Loki/OpenTelemetry e alertas SRE.
- **Deploy:** Docker Compose para MVP, Kubernetes/K3s para escala, GitHub Actions para CI/CD.

## 1.6 Arquitetura edge

- **Nível 0:** ESP32-S3 faz leitura, compressão leve, estatísticas de áudio, contagem e deep sleep.
- **Nível 1:** gateway rural opcional consolida colmeias próximas, guarda dados offline e executa inferência leve.
- **Nível 2:** cloud faz análise pesada, geoespacial, treino ML e relatórios.

## 1.7 Arquitetura mobile

- React Native/Expo ou Flutter.
- Offline-first com banco local SQLite/WatermelonDB/Realm.
- Sincronização incremental por `updated_at` e fila local de ações.
- Push notifications para alertas críticos.
- Upload de fotos com compressão e retry.
- Geolocalização para cadastro de apiários e auditoria de manejo.

## 1.8 Arquitetura de IA

```text
Dados IoT + imagens + áudio + Copernicus
        │
        ├─ Feature store: médias, deltas, sazonalidade, índices orbitais
        ├─ Modelos tabulares: Isolation Forest, XGBoost, Random Forest
        ├─ Séries temporais: Prophet, LSTM/TCN, regressão robusta
        ├─ Visão: YOLOv8/YOLOv11, segmentação, classificação de favo
        ├─ Áudio: MFCC, espectrograma, CNN leve, detecção de stress
        └─ Motor de alertas: regras explicáveis + score probabilístico
```

## 1.9 Arquitetura geoespacial

- Geometria central: `hive.location` como `POINT` PostGIS.
- Área de voo: `ST_Buffer(location::geography, 3000)`.
- Camadas raster: NDVI, NDWI, EVI, ERA5, Sentinel-5P e uso do solo.
- Armazenamento: estatísticas por buffer no PostGIS; rasters brutos em object storage; metadados no banco.
- APIs: GeoJSON, vector tiles, WMS/WMTS opcional, endpoints REST geoespaciais.

---

# 2. Roadmap Completo de Desenvolvimento

## Fase 1 → MVP técnico

- **Tempo estimado:** 0 a 8 semanas.
- **Objetivos:** provar ingestão IoT, dashboard básico, Copernicus sintético/real, visão computacional inicial e alerta simples.
- **Entregas:**
  - firmware ESP32-S3 com payload versionado;
  - broker MQTT local/cloud;
  - backend FastAPI mínimo;
  - PostgreSQL/PostGIS;
  - dashboard Streamlit ou web básico;
  - integração Sentinel Hub com fallback;
  - app mobile consumindo dados reais ou mockados;
  - pipeline YOLO CLI para foto de favo.
- **Dependências:** sensores funcionais, credenciais Sentinel Hub, ambiente Docker, contratos JSON.
- **Equipe:** CTO full stack, 1 IoT, 1 backend/data, 1 mobile/frontend, 1 cientista/geo parcial.
- **Prioridades:** confiabilidade do dado, baixo consumo, API mínima, demo executável.
- **Riscos técnicos:** internet rural instável, calibração de sensores, credenciais Copernicus, modelo visual sem dataset suficiente.

## Fase 2 → MVP funcional

- **Tempo estimado:** 2 a 4 meses.
- **Objetivos:** piloto com 5 a 20 colmeias, app operacional, alertas úteis e laudos visuais.
- **Entregas:**
  - autenticação e multi-tenant inicial;
  - cadastro de fazendas/apiários/colmeias;
  - telemetria real em séries temporais;
  - alertas configuráveis;
  - mapas com buffer de 3 km;
  - upload de imagens pelo app;
  - job Copernicus agendado;
  - relatórios ESG simples;
  - observabilidade básica.
- **Dependências:** hardware v1, conectividade em campo, UX validada com produtores.
- **Equipe:** 5 a 7 pessoas.
- **Prioridades:** operação em campo e feedback do apicultor.
- **Riscos:** suporte técnico, ruído nos dados, perda de pacotes, falsa sensação de precisão científica.

## Fase 3 → Plataforma beta

- **Tempo estimado:** 4 a 7 meses.
- **Objetivos:** beta B2B/B2G com governança de dados, dashboard ESG e APIs.
- **Entregas:**
  - RBAC completo;
  - integração ERA5 e Sentinel-5P;
  - MLOps com versionamento de modelos;
  - feature store;
  - marketplace beta;
  - notificações push;
  - relatórios PDF;
  - auditoria LGPD;
  - deploy Kubernetes ou PaaS escalável.
- **Dependências:** métricas validadas, base piloto, termos de uso e política de privacidade.
- **Equipe:** 8 a 10 pessoas.
- **Prioridades:** confiabilidade, compliance, documentação e UX.
- **Riscos:** custo cloud, complexidade multi-tenant, drift de modelos.

## Fase 4 → Escalabilidade

- **Tempo estimado:** 7 a 10 meses.
- **Objetivos:** operar centenas a milhares de colmeias.
- **Entregas:**
  - arquitetura orientada a eventos;
  - particionamento temporal;
  - cache geoespacial;
  - edge gateway;
  - OTA firmware;
  - plano de backup e disaster recovery;
  - dashboards de saúde operacional.
- **Dependências:** contratos estáveis, hardware revisado, automação CI/CD.
- **Equipe:** 10 a 14 pessoas.
- **Prioridades:** custo por colmeia, observabilidade e suporte.
- **Riscos:** escalada de storage, simultaneidade MQTT, suporte de campo.

## Fase 5 → Operação comercial

- **Tempo estimado:** 10 a 12+ meses.
- **Objetivos:** comercialização SaaS/hardware/API/ESG.
- **Entregas:**
  - billing e planos;
  - SLAs;
  - contratos B2B/B2G;
  - marketplace transacional;
  - certificação ou parceria científica;
  - API externa paga;
  - operação internacional preparada.
- **Dependências:** validação científica, estabilidade operacional, playbook de instalação.
- **Equipe:** 14+ pessoas incluindo suporte, vendas técnicas e parcerias.
- **Prioridades:** receita recorrente, confiabilidade e governança.
- **Riscos:** compliance internacional, suporte logístico e custo de hardware.

---

# 3. Estrutura Completa do Backend

## 3.1 Stack recomendada

- **Linguagem:** Python 3.12 para backend, ETL e IA.
- **Framework:** FastAPI com Pydantic v2.
- **Banco:** PostgreSQL 16 + PostGIS; TimescaleDB opcional para séries temporais.
- **Cache/fila curta:** Redis.
- **MQTT:** EMQX para produção; Mosquitto para MVP/local.
- **Processamento assíncrono:** Celery + Redis/RabbitMQ ou Dramatiq; para escala, Kafka/Redpanda.
- **WebSocket:** FastAPI WebSocket ou Socket.IO para alertas em tempo real.
- **Containers:** Docker e Docker Compose no MVP; Kubernetes depois.
- **CI/CD:** GitHub Actions com lint, testes, build, migrations e deploy.

## 3.2 Microsserviços por maturidade

### MVP: modular monolith

Um único backend FastAPI com módulos:

```text
backend/app/
├── api/v1/
├── auth/
├── tenants/
├── farms/
├── apiaries/
├── hives/
├── devices/
├── telemetry/
├── geospatial/
├── copernicus/
├── vision/
├── alerts/
├── esg/
├── marketplace/
├── workers/
└── shared/
```

### Escala: serviços separados

- `identity-service`: usuários, tenants, RBAC.
- `iot-ingestion-service`: MQTT/HTTP, validação e roteamento.
- `telemetry-service`: séries temporais, agregações e WebSocket.
- `geo-service`: PostGIS, buffers, tiles e Copernicus.
- `ml-service`: inferência, feature store e alertas.
- `vision-service`: upload, YOLO, laudos e imagens.
- `notification-service`: push, e-mail, WhatsApp/SMS.
- `marketplace-service`: catálogo, pedidos, pagamentos.
- `reporting-service`: PDF, ESG, exportações.

## 3.3 Autenticação e autorização

- OAuth2/OIDC com Keycloak, Auth0, Cognito ou Supabase Auth.
- JWT curto para APIs; refresh token seguro.
- RBAC por tenant:
  - `owner`: dono da organização;
  - `admin`: gerencia usuários e fazendas;
  - `technician`: manejo e laudos;
  - `beekeeper`: operação diária;
  - `viewer`: leitura ESG;
  - `api_client`: integração B2B.
- Dispositivos usam `device_id`, certificado ou token rotativo.

## 3.4 APIs REST

- Versionamento: `/api/v1`.
- Padrão de recursos:
  - `GET /hives`
  - `POST /hives`
  - `GET /hives/{id}`
  - `PATCH /hives/{id}`
  - `GET /hives/{id}/telemetry?from=&to=&metric=`
  - `GET /hives/{id}/alerts`
  - `POST /vision/inferences`
- Contratos com Pydantic; respostas paginadas; filtros por tenant; idempotência em ingestão.

## 3.5 APIs geoespaciais

- `GET /geo/hives.geojson`
- `GET /geo/hives/{id}/buffer?radius_km=3`
- `GET /geo/hives/{id}/indices?index=ndvi&period=last_30d`
- `GET /geo/tiles/{z}/{x}/{y}.pbf`
- `GET /geo/territories/{id}/risk-score`

Usar PostGIS para `ST_DWithin`, `ST_Intersects`, `ST_Buffer`, `ST_AsGeoJSON` e índices GiST.

## 3.6 Ingestão IoT

Tópicos MQTT:

```text
beespace/v1/{tenant_id}/{device_id}/telemetry
beespace/v1/{tenant_id}/{device_id}/events
beespace/v1/{tenant_id}/{device_id}/health
beespace/v1/{tenant_id}/{device_id}/commands
beespace/v1/{tenant_id}/{device_id}/ota
```

Payload mínimo:

```json
{
  "schema_version": "1.0",
  "message_id": "uuid",
  "device_id": "BS-ESP32-0001",
  "hive_id": "BS-HIVE-0001",
  "timestamp": "2026-06-07T12:00:00Z",
  "battery": {"voltage_v": 3.92, "percent": 78},
  "environment": {"temperature_c": 34.5, "humidity_percent": 58, "pressure_hpa": 1012, "luminosity_lux": 7400},
  "production": {"weight_kg": 41.2},
  "activity": {"entries": 182, "exits": 176},
  "audio": {"rms": 0.21, "peak": 0.73, "zcr": 0.12},
  "location": {"lat": -23.55, "lon": -46.63, "fix": true},
  "flags": {"offline_buffered": false, "tamper": false}
}
```

## 3.7 Processamento de telemetria

1. Validar schema e assinatura.
2. Resolver `device_id` para tenant/colmeia.
3. Descartar duplicatas por `message_id`.
4. Persistir leitura bruta.
5. Normalizar métricas em tabela de série temporal.
6. Gerar agregados por 5 min, 1 h e 1 dia.
7. Rodar regras rápidas de alerta.
8. Enfileirar IA e geoespacial.
9. Notificar dashboards se necessário.

## 3.8 Multi-tenant SaaS

- Todas as tabelas de negócio possuem `tenant_id`.
- Políticas de Row Level Security no PostgreSQL para dados sensíveis.
- Separação por tenant lógico no MVP; tenants grandes podem migrar para banco dedicado.
- Auditoria de acesso a dados ambientais e imagens.
- Planos por quantidade de colmeias, usuários, retenção e recursos ESG/API.

## 3.9 Segurança, LGPD e versionamento

- Dados pessoais minimizados; geolocalização tratada como dado sensível de negócio.
- Consentimento para uso de dados em pesquisa e modelos.
- Criptografia em trânsito e repouso.
- Versionamento de API, payload IoT e modelos ML.
- Política de retenção: telemetria bruta menor, agregados mais longos.

---

# 4. Infraestrutura IoT e Hardware

## 4.1 Arquitetura eletrônica

```text
Painel solar -> controlador carga/BMS -> bateria -> regulador buck/boost -> ESP32-S3
                                                                  │
                                                                  ├─ I2C: BME280, BH1750, MPU6050
                                                                  ├─ ADC: bateria, sensores analógicos
                                                                  ├─ HX711: célula de carga
                                                                  ├─ I2S: microfone INMP441
                                                                  ├─ GPIO/interrupt: TCRT5000 entrada/saída
                                                                  ├─ UART: GPS NEO-6M/alternativo
                                                                  ├─ SPI/I2C: SD/FRAM opcional
                                                                  └─ rádio: Wi-Fi/BLE; LoRa/4G via módulo opcional
```

## 4.2 ESP32/ESP8266

- **ESP32-S3 recomendado:** melhor RAM, I2S, FreeRTOS, OTA e edge AI leve.
- **ESP32 clássico:** aceitável para nós simples.
- **ESP8266:** apenas para protótipos de baixa complexidade; não recomendado para áudio/edge.

## 4.3 Lista completa de componentes

- ESP32-S3 DevKit ou módulo customizado.
- BME280 ou SHT31: temperatura, umidade, pressão.
- BH1750: luminosidade externa.
- HX711 + 4 células de carga ou célula única dimensionada.
- INMP441 I2S: bioacústica.
- TCRT5000 ou sensor IR de barreira: entrada/saída.
- MPU6050/ICM-20948: movimento e antifurto.
- GPS NEO-6M/ATGM336H com MOSFET para corte de energia.
- Módulo LoRa SX1276/SX1262 opcional.
- Modem LTE-M/NB-IoT/4G opcional para áreas remotas.
- MicroSD ou FRAM para buffer offline.
- Bateria LiFePO4 ou 18650 protegida.
- Painel solar 5-10 W por nó, conforme consumo.
- Controlador de carga solar e BMS.
- Caixa IP65/IP67, prensa-cabos, proteção contra umidade e propólis.
- Conectores JST/M12, fusível, TVS e proteção contra inversão.

## 4.4 Comunicação e protocolos

- Wi-Fi quando disponível.
- LoRa ponto-a-ponto para gateway rural.
- LoRaWAN quando houver cobertura.
- LTE-M/NB-IoT/4G para clientes premium ou sem gateway.
- MQTT/TLS como protocolo principal.
- HTTPS como fallback para envio em lote.
- BLE para configuração local pelo app.

## 4.5 Fluxo de dados do hardware

```text
Wake -> leitura rápida bateria -> decide modo
  ├─ modo normal: sensores ambientais + peso + contadores + áudio resumido
  ├─ modo evento: antifurto, fluxo extremo, queda de peso, abertura de tampa
  ├─ modo manutenção: BLE/configuração/calibração
  └─ modo emergência: GPS + pacote prioritário
-> monta payload -> tenta publicar -> se falhar grava buffer -> deep sleep
```

## 4.6 Lógica embarcada

- Ciclo padrão a cada 15 minutos.
- Leituras de baixo consumo primeiro; sensores caros energizados sob demanda.
- Média/mediana local para reduzir ruído.
- Áudio: calcular RMS, pico, ZCR e espectrograma curto se gateway disponível.
- Peso: tara e filtro contra vibração.
- Offline: fila circular em flash/SD com `message_id` e timestamp.
- Fail-safe: watchdog, brownout detection, rollback OTA.
- Configuração remota: intervalo, thresholds, tópicos MQTT e modo de energia.

## 4.7 Pipeline de firmware

1. Definir contrato de payload.
2. Implementar drivers e calibração.
3. Criar testes de bancada.
4. Medir consumo em deep sleep, coleta e transmissão.
5. Validar caixa em ambiente úmido/quente.
6. Implementar OTA assinado.
7. Criar matriz de versões firmware/hardware.
8. Documentar instalação de campo.

## 4.8 Colmeia como estação autônoma de biovigilância

A colmeia torna-se um biossensor quando os sinais de atividade biológica são combinados ao contexto ambiental. Temperatura interna, umidade, acústica, peso e fluxo de abelhas indicam estabilidade da colônia. NDVI, NDWI, clima e poluentes indicam pressão externa. O sistema deve sempre traduzir correlações em ações: inspecionar, alimentar, mover apiário, verificar doença, proteger contra calor, avaliar contaminação ou documentar impacto ESG.

---

# 5. Pipeline de Dados Copernicus

## 5.1 Fontes prioritárias

- **Sentinel Hub API:** acesso rápido a Sentinel-2 por Process API.
- **Copernicus Data Space Ecosystem:** catálogo, downloads e APIs oficiais.
- **Sentinel-2 L2A:** NDVI, NDWI, EVI, índices de vegetação e água.
- **Sentinel-5P:** NO2, SO2, CO, O3, aerossóis e poluição atmosférica.
- **ERA5/C3S:** temperatura, precipitação, vento, umidade, radiação e extremos climáticos.
- **CLMS/Land Cover:** uso e cobertura do solo, vegetação e fragmentação.

## 5.2 Índices

- **NDVI:** vigor da vegetação: `(B08 - B04) / (B08 + B04)`.
- **NDWI:** água/umidade vegetal: `(B03 - B08) / (B03 + B08)`.
- **EVI:** vegetação robusta em áreas densas: `2.5*(NIR-Red)/(NIR+6*Red-1.5*Blue+1)`.
- **Uso do solo:** floradas potenciais, monocultura, mata, água, urbano e áreas degradadas.

## 5.3 Recorte geográfico e buffer de 3 km

- Cada colmeia possui ponto geográfico WGS84.
- O raio de voo padrão é 3 km, equivalente a cerca de 2.827 hectares.
- Produção deve usar `ST_Buffer(geography, 3000)` e reprojeções adequadas.
- Para múltiplas colmeias, dissolver buffers por apiário para reduzir custo.

## 5.4 Fluxo completo do pipeline orbital

```text
Scheduler diário/semanal
  -> seleciona hives/apiaries ativos
  -> calcula buffer 3 km ou território
  -> consulta catálogo Copernicus/Sentinel Hub
  -> filtra nuvem e qualidade
  -> processa índices NDVI/NDWI/EVI
  -> agrega estatísticas por buffer: média, mediana, p10, p90, desvio
  -> compara com histórico: 7, 14, 30, 90 dias
  -> salva metadados e rasters
  -> atualiza scores ambientais
  -> dispara alertas se houver queda crítica ou risco climático
```

## 5.5 Arquitetura ETL geoespacial

- **Extract:** APIs Copernicus, Sentinel Hub, ERA5, Sentinel-5P.
- **Transform:** rasterio/xarray/rioxarray, geopandas, shapely, pyproj, Dask para escala.
- **Load:** PostGIS para estatísticas e object storage para rasters.
- **Cache:** chave por `tenant_id`, `hive_id/apiary_id`, `index`, `period`, `bbox_hash`.

## 5.6 Modelo de armazenamento espacial

- `geo_index_observations`: estatísticas por data e área.
- `geo_raster_assets`: ponteiros para GeoTIFF/COG no S3.
- `land_cover_snapshots`: classes de uso do solo por área.
- `climate_observations`: ERA5 agregado por ponto/buffer.
- `pollution_observations`: Sentinel-5P agregado por área.

## 5.7 Correlação orbital-biológica

- Cruzar queda de NDVI com queda de peso e redução de fluxo.
- Cruzar NDWI baixo e ERA5 calor com alta temperatura interna.
- Cruzar poluição/aerossóis com redução de forrageamento.
- Cruzar uso do solo com risco de intoxicação e perda de florada.
- Usar janelas temporais defasadas: 1, 3, 7, 14 e 30 dias.
- Não afirmar causalidade sem validação; classificar como indício, correlação ou alerta preventivo.

---

# 6. Inteligência Artificial e Machine Learning

## 6.1 Arquitetura de IA

```text
Coleta -> Validação -> Feature Store -> Treino/Inferência -> Explicação -> Alerta -> Feedback humano
```

## 6.2 Visão computacional

- YOLO para detectar classes em favos: mel, néctar, pólen, ovos, larvas e crias operculadas.
- OpenCV para pré-processamento: correção de iluminação, blur detection, crop e anotação.
- Roboflow para anotação, versionamento de dataset e augmentations.
- Produção: endpoint recebe imagem, valida qualidade, roda inferência, salva laudo e retorna percentuais.

## 6.3 Datasets

- Fotos de favos por região, espécie/raça, iluminação, estágio de produção e época do ano.
- Telemetria longitudinal por colmeia.
- Áudio com estados conhecidos: normal, stress, enxameação, rainha ausente, manejo.
- Dados orbitais por buffer.
- Labels humanos de eventos: alimentação, colheita, inspeção, doença, pesticida, troca de rainha.

## 6.4 Treinamento

- Começar com modelos explicáveis: Isolation Forest e regras.
- Evoluir para XGBoost/LightGBM com labels reais.
- Para séries temporais: baseline com médias móveis, depois Prophet/TCN/LSTM.
- Para áudio: MFCC + Random Forest no MVP; CNN em espectrogramas na beta.
- Para visão: YOLO treinado e validado com mAP, precision, recall por classe.

## 6.5 Inferência

- Cloud para visão e modelos pesados.
- Edge para estatísticas, anomalias simples e áudio resumido.
- Gateway com modelos ONNX/TFLite quando internet for crítica.
- Resposta sempre com explicabilidade: quais features contribuíram.

## 6.6 MLOps

- MLflow para experimentos e model registry.
- DVC para datasets grandes e metadados.
- Versionamento de modelo ligado a dataset, parâmetros, métricas e data.
- Monitoramento de drift por região e sazonalidade.
- Aprovação humana antes de promover modelo para produção.

## 6.7 Validação científica

- Separar validação técnica de validação biológica.
- Medir falsos positivos/negativos de alertas.
- Comparar com inspeções de apicultores e pesquisadores.
- Publicar metodologia e limites de confiança.

## 6.8 Sistema de alertas ambientais inteligentes

Camadas:

1. **Regras críticas:** bateria baixa, temperatura extrema, perda brusca de peso.
2. **Anomalia estatística:** comportamento fora do padrão da colmeia.
3. **Correlação ambiental:** queda NDVI/NDWI + sinais internos.
4. **Predição:** risco futuro de stress, baixa produtividade ou perda de florada.
5. **Feedback:** usuário confirma/nega; o sistema aprende.

Cada alerta deve conter severidade, evidências, confiança, ação recomendada, prazo e origem dos dados.

---

# 7. Aplicativos BeeSpace

## 7.1 BeeSpace Monitor

Funcionalidades:

- Login e seleção de tenant.
- Cadastro de fazenda, apiário e colmeia.
- Onboarding de dispositivo via BLE/QR Code.
- Telemetria em cards: temperatura, umidade, peso, bateria, fluxo, áudio.
- Mapa de colmeias e buffer de voo.
- Alertas com severidade e ação sugerida.
- Registro de manejo: inspeção, alimentação, troca de rainha, colheita.
- Upload de imagens de favos.
- Laudo visual com percentuais.
- Sincronização offline.
- Push notifications.

Telas:

- Splash/onboarding.
- Login.
- Lista de fazendas/apiários.
- Mapa.
- Detalhe da colmeia.
- Histórico e gráficos.
- Alertas.
- Registro de manejo.
- Captura de foto.
- Laudo YOLO.
- Configuração de dispositivo.

## 7.2 BeeSpace Marketplace

Funcionalidades:

- Catálogo de mel, própolis, rainhas, equipamentos e serviços.
- Perfil de produtor.
- Feed social técnico.
- Mensageria entre produtores/compradores.
- Pagamentos via Stripe/Mercado Pago/Pix.
- Avaliações.
- Integração com laudos/ESG como diferencial de procedência.
- Logística e status de pedidos.

## 7.3 Arquitetura mobile recomendada

React Native/Expo é coerente com o app existente. Flutter é excelente para UI, mas migrar agora aumenta custo. Recomendação: manter React Native/Expo no MVP e reavaliar apenas se houver demanda forte por performance específica.

Estrutura:

```text
apps/mobile/src/
├── app/ or screens/
├── components/
├── features/
│   ├── auth/
│   ├── hives/
│   ├── telemetry/
│   ├── alerts/
│   ├── vision/
│   ├── marketplace/
│   └── settings/
├── services/
├── state/
├── storage/
├── navigation/
├── theme/
└── utils/
```

Estado:

- TanStack Query para cache de API.
- Zustand ou Redux Toolkit para estado global.
- SQLite/WatermelonDB para offline-first.
- Expo Notifications para push.

APIs mobile:

- `GET /me`
- `GET /farms`
- `GET /apiaries`
- `GET /hives`
- `GET /hives/{id}/snapshot`
- `GET /hives/{id}/telemetry`
- `POST /hives/{id}/management-events`
- `POST /vision/inferences`
- `GET /alerts`
- `PATCH /alerts/{id}/acknowledge`

---

# 8. Dashboard ESG e Inteligência Ambiental

## 8.1 Dashboards

- Visão executiva ESG.
- Monitoramento operacional do apiário.
- Saúde de colmeias.
- Risco climático.
- Cobertura vegetal e água.
- Alertas e incidentes.
- Produtividade e manejo.
- Marketplace e impacto econômico.

## 8.2 Mapas

- Mapa interativo com colmeias, apiários e buffers.
- Heatmap de risco ambiental.
- Camadas NDVI/NDWI/EVI.
- Uso do solo.
- Eventos de manejo.
- Áreas com queda de vegetação.

## 8.3 KPIs ambientais e ESG

- Área monitorada por colmeias.
- Bee Environmental Health Score.
- Índice de vigor vegetal médio.
- Variação de NDVI/NDWI.
- Número de alertas críticos resolvidos.
- Tempo médio de resposta a alertas.
- Colmeias ativas e disponibilidade de telemetria.
- Produtividade por colmeia/apiário.
- Indicadores de biodiversidade proxy.
- Evidências contra greenwashing: trilhas de dados, origem, datas e metodologia.

## 8.4 Gráficos e relatórios

- Séries temporais multi-eixo.
- Boxplots por apiário.
- Mapas temporais.
- Comparação antes/depois de intervenção.
- Relatórios PDF automáticos mensais.
- Exportação CSV/GeoJSON.
- Relatórios B2B com metodologia, limites e evidências.

---

# 9. Banco de Dados Completo

## 9.1 Entidades principais

```text
Tenant -> Users -> Farms -> Apiaries -> Hives -> Devices -> Sensors -> Telemetry
                                      └-> Management Events
                                      └-> Vision Inferences
                                      └-> Alerts
                                      └-> Geo Observations
Marketplace: Sellers -> Products -> Orders -> Payments
ESG: Reports -> Metrics -> Evidence
Audit: Logs -> API Keys -> Device Credentials
```

## 9.2 Tabelas recomendadas

- `tenants(id, name, plan, country, created_at)`
- `users(id, tenant_id, email, name, role, status, created_at)`
- `farms(id, tenant_id, name, owner_name, geom, address, metadata)`
- `apiaries(id, tenant_id, farm_id, name, geom, notes)`
- `hives(id, tenant_id, apiary_id, code, name, geom, status, installed_at)`
- `devices(id, tenant_id, hive_id, serial, firmware_version, hardware_version, status, last_seen_at)`
- `sensors(id, device_id, type, model, calibration_json, installed_at)`
- `telemetry_raw(id, tenant_id, device_id, hive_id, message_id, payload_json, received_at)`
- `telemetry_points(time, tenant_id, hive_id, metric, value, unit, quality)`
- `telemetry_snapshots(id, hive_id, timestamp, temperature_c, humidity_percent, weight_kg, battery_percent, bee_entries, bee_exits, audio_rms)`
- `alerts(id, tenant_id, hive_id, type, severity, status, confidence, title, description, evidence_json, created_at, acknowledged_at)`
- `management_events(id, tenant_id, hive_id, user_id, type, notes, occurred_at, photos)`
- `vision_images(id, tenant_id, hive_id, user_id, object_key, captured_at, quality_score)`
- `vision_inferences(id, image_id, model_version, status, results_json, created_at)`
- `ml_models(id, name, version, type, metrics_json, artifact_uri, status)`
- `geo_index_observations(id, tenant_id, hive_id, index_name, period_start, period_end, stats_json, geom)`
- `geo_raster_assets(id, observation_id, object_key, cog_url, bbox, metadata_json)`
- `climate_observations(id, tenant_id, hive_id, source, variable, timestamp, value, unit)`
- `pollution_observations(id, tenant_id, hive_id, source, variable, timestamp, value, unit)`
- `esg_reports(id, tenant_id, period_start, period_end, status, pdf_key, metrics_json)`
- `marketplace_products(id, tenant_id, seller_id, title, category, price, currency, stock, status)`
- `marketplace_orders(id, tenant_id, buyer_id, seller_id, status, total, created_at)`
- `audit_logs(id, tenant_id, actor_id, action, resource_type, resource_id, ip, metadata_json, created_at)`

## 9.3 Índices

- GiST em geometrias: `farms.geom`, `apiaries.geom`, `hives.geom`, `geo_index_observations.geom`.
- BRIN ou Timescale hypertable para `telemetry_points.time`.
- B-tree em `tenant_id`, `hive_id`, `device_id`, `created_at`.
- Unique em `telemetry_raw.message_id`.
- JSONB GIN para `payload_json`, `evidence_json`, `metadata_json` quando necessário.
- Particionamento por tempo em telemetria bruta.

## 9.4 Otimização para geodados

- Usar `geography` para distância real em metros quando necessário.
- Usar `geometry` com SRID correto para operações e tiles.
- Pré-computar buffers por colmeia/apiário.
- Agregar estatísticas orbitais por área para evitar reprocessar rasters.
- Guardar COGs em object storage e servir por CDN quando público/autorizado.

---

# 10. Segurança e Confiabilidade

## 10.1 Autenticação

- OAuth2/OIDC para usuários.
- JWT curto e refresh tokens protegidos.
- API keys com escopo para B2B.
- Tokens/certificados por dispositivo.

## 10.2 Segurança IoT

- MQTT sobre TLS.
- Credenciais únicas por dispositivo.
- Rotação e revogação de credenciais.
- OTA assinado.
- Secure boot e flash encryption em versões avançadas.
- Tópicos MQTT com ACL por tenant/dispositivo.

## 10.3 Criptografia

- TLS 1.2+ em trânsito.
- Criptografia em repouso no banco e object storage.
- Hash seguro para senhas quando auth próprio for usado.
- Secrets em Vault/Secret Manager, nunca no repositório.

## 10.4 LGPD

- Mapear dados pessoais e dados sensíveis de localização.
- Obter consentimento para dados do produtor e uso científico.
- Minimizar coleta pessoal.
- Permitir exportação e exclusão quando aplicável.
- Registrar bases legais para cada processamento.

## 10.5 Auditoria e observabilidade

- Log de login, exportação, mudança de permissão, criação de API key e acesso a relatórios.
- Tracing distribuído com OpenTelemetry.
- Métricas de ingestão, latência, erro e disponibilidade.
- Alertas operacionais: broker offline, fila acumulada, disco alto, ingestão parada.

## 10.6 Backup, redundância e tolerância a falhas

- Backups diários do PostgreSQL e testes mensais de restore.
- Object storage com versionamento.
- Redis sem dados críticos ou com persistência quando necessário.
- Broker MQTT em cluster na escala.
- Retry idempotente para ingestão.
- Edge buffer para falhas de internet.

---

# 11. DevOps e Deploy

## 11.1 Ambientes

- `local`: Docker Compose.
- `dev`: branch de desenvolvimento com banco separado.
- `staging`: espelha produção com dados sintéticos.
- `production`: alta disponibilidade, backups e monitoramento.

## 11.2 Docker

Serviços MVP:

```text
postgres-postgis
redis
mqtt-broker
backend-fastapi
worker
streamlit-dashboard
frontend-web
```

## 11.3 Kubernetes

- Deployments para backend, workers, dashboard e frontend.
- StatefulSets ou serviços gerenciados para banco/broker.
- HPA por CPU, memória e métricas de fila.
- Ingress com TLS.
- Secrets via External Secrets.

## 11.4 CI/CD com GitHub Actions

Pipeline:

```text
pull request
  -> lint backend
  -> testes unitários
  -> type check
  -> build Docker
  -> smoke tests
  -> migrations dry-run
merge main
  -> build/push images
  -> deploy staging
  -> smoke staging
  -> aprovação manual
  -> deploy production
  -> migrações
  -> health checks
  -> notificação
```

## 11.5 Observabilidade

- Prometheus para métricas.
- Grafana para dashboards.
- Loki ou CloudWatch/Stackdriver para logs.
- Sentry para erros de backend/frontend/mobile.
- Uptime Kuma ou Better Stack para disponibilidade.

## 11.6 Cloud recomendada

- **MVP baixo custo:** Railway/Supabase + Cloudflare + object storage S3 compatível.
- **Produção AWS:** ECS/EKS, RDS Postgres/PostGIS, ElastiCache, S3, IoT Core/EMQX, CloudFront.
- **Produção GCP:** Cloud Run/GKE, Cloud SQL, Memorystore, Cloud Storage, Pub/Sub.
- **Azure:** AKS, PostgreSQL Flexible Server, Blob Storage, Event Grid.
- **Supabase:** excelente para prototipar Postgres/Auth/Storage, mas avaliar limites para IoT pesado.

---

# 12. Estratégia de Escalabilidade

## 12.1 Escalar para milhares de colmeias

- Reduzir frequência de envio conforme estabilidade.
- Enviar agregados locais em vez de sinais brutos contínuos.
- Usar MQTT QoS adequado: QoS 1 para eventos importantes; QoS 0 para métricas frequentes não críticas.
- Separar ingestão de processamento por filas.
- Particionar telemetria por tempo e tenant.
- Cache de snapshots atuais por hive em Redis.

## 12.2 Arquitetura orientada a eventos

Eventos:

- `TelemetryReceived`
- `HiveSnapshotUpdated`
- `AnomalyDetected`
- `GeoIndexUpdated`
- `AlertCreated`
- `VisionInferenceCompleted`
- `ReportGenerated`

## 12.3 Edge nodes

- Gateway local por apiário/fazenda.
- Sincronização compactada em lote.
- Inferência de anomalia local.
- Store-and-forward.
- OTA e configuração distribuída.

## 12.4 Compressão e custos

- JSON compacto no MVP; CBOR/MessagePack em escala.
- Agrupar leituras offline.
- Retenção: bruto 30-90 dias; agregados 2-5 anos.
- Rasters em COG com compressão.
- Consultas Copernicus por apiário em vez de colmeia quando buffers sobrepõem.

## 12.5 Multi-região e CDN

- CDN para frontend, imagens e COGs.
- Banco primário por região com réplicas de leitura.
- Separação por país em produção internacional.
- Observância de residência de dados conforme mercado.

---

# 13. Cronograma Técnico de 12 Meses

## Mês 1

- Sprint 1: contratos de payload, setup Docker, FastAPI mínimo, PostGIS, MQTT local.
- Sprint 2: firmware coleta sensores principais, dashboard básico e simulador conectado.
- Milestone: telemetria de bancada chegando ao banco.
- Testes: payload, duplicidade, consumo básico.

## Mês 2

- Sprint 3: app mobile lê snapshot, cadastro manual de colmeia, alertas básicos.
- Sprint 4: Sentinel Hub/fallback, buffer 3 km, NDVI/NDWI no dashboard.
- Milestone: demo ponta a ponta.
- Testes: campo curto com 1-2 colmeias.

## Mês 3

- Sprint 5: upload de imagens e pipeline YOLO CLI/API.
- Sprint 6: relatórios simples, regras de alerta e logging.
- Milestone: MVP 90 dias.
- Testes: validação com apicultor e revisão científica inicial.

## Mês 4

- Autenticação, tenants, RBAC inicial.
- Cadastro fazenda/apiário/colmeia.
- App offline-first v1.
- Firmware buffer offline.
- Piloto 5-10 colmeias.

## Mês 5

- Jobs assíncronos, agregações e WebSocket.
- Notificações push.
- Calibração formal de peso/temperatura.
- Dashboard ESG v1.

## Mês 6

- ERA5 e Sentinel-5P.
- Feature store inicial.
- MLOps com MLflow.
- Visão computacional com dataset versionado.
- Piloto 20 colmeias.

## Mês 7

- Marketplace beta catálogo.
- Relatórios PDF.
- Auditoria LGPD.
- Edge gateway protótipo.
- OTA firmware.

## Mês 8

- Escala backend: filas robustas, particionamento, cache.
- Mapas vetoriais/tiles.
- API pública beta.
- Teste de carga com simulador de 1.000 colmeias.

## Mês 9

- Modelos preditivos com labels reais.
- Drift monitoring.
- Gateway rural em campo.
- SLOs e runbooks.

## Mês 10

- Billing, planos SaaS e permissões avançadas.
- Marketplace transacional.
- Contratos B2B/B2G piloto.
- Segurança avançada IoT.

## Mês 11

- Multi-região preparada.
- Relatórios ESG auditáveis.
- Documentação API e SDK.
- Certificação/parcerias científicas.

## Mês 12

- Hardening comercial.
- SLAs, suporte, playbook de instalação.
- Operação com 100-500 colmeias.
- Plano de expansão internacional.

---

# 14. Estrutura da Equipe Técnica

## Papéis

- **CTO:** arquitetura, priorização, contratação, governança técnica e decisões build/buy.
- **Backend engineer:** FastAPI, banco, APIs, ingestão e segurança.
- **Frontend engineer:** dashboard web, mapas, visualizações e relatórios.
- **Mobile engineer:** app Monitor/Marketplace, offline-first e push.
- **IoT/embedded engineer:** firmware, hardware, energia, OTA e testes de campo.
- **ML/AI engineer:** visão, anomalias, MLOps e inferência.
- **Data scientist:** métricas ambientais, validação, estatística e modelos.
- **Geospatial engineer:** Copernicus, PostGIS, raster/vector, ERA5/Sentinel.
- **DevOps/SRE:** CI/CD, deploy, observabilidade, segurança e custo cloud.
- **UX/UI:** fluxos para produtor rural e dashboard ESG.
- **QA:** testes, automação, campo e regressão.
- **Scientific advisor:** protocolo experimental, validação biológica e publicações.

## Fluxo de trabalho

- Scrum/Kanban híbrido.
- Sprints quinzenais.
- Demo quinzenal com stakeholders.
- Backlog por épicos: IoT, backend, geo, IA, mobile, ESG, marketplace.
- ADRs para decisões arquiteturais.
- Definition of Done: teste, observabilidade, documentação, segurança e deploy.

---

# 15. MVP Realista para os Primeiros 90 Dias

## Priorizar

1. Hardware funcional com sensores essenciais.
2. Ingestão MQTT para backend.
3. Banco PostGIS e telemetria.
4. Dashboard básico com mapa e séries temporais.
5. Copernicus NDVI/NDWI com fallback.
6. Alertas por regras explicáveis.
7. App simples para ver colmeia e alerta.
8. Visão computacional inicial via upload manual.

## Não desenvolver ainda

- Marketplace transacional completo.
- Billing SaaS.
- Blockchain/BeeCoin em produção.
- Modelos deep learning complexos para séries temporais.
- Multi-região.
- API pública paga.
- Certificação ESG formal sem dados validados.

## Pode ser mockado

- Alguns dados Copernicus quando não houver credenciais.
- Visão computacional com resultados sintéticos até dataset robusto.
- Push notifications podem começar como alertas no app/dashboard.
- Pagamentos e marketplace podem ser protótipos navegáveis.
- Gateway rural pode ser simulado com laptop/Raspberry Pi.

## Entregáveis dos 90 dias

- 2-3 colmeias instrumentadas em bancada/campo.
- Backend FastAPI com ingestão, telemetria e alertas.
- Dashboard Streamlit/web.
- App mobile Expo com snapshot e alertas.
- Pipeline YOLO executável.
- Documento de metodologia científica inicial.
- Métricas de consumo de energia e confiabilidade.

---

# 16. Tecnologias Recomendadas

| Tecnologia | Função | Vantagens | Custo | Escalabilidade | Complexidade |
|---|---|---|---|---|---|
| FastAPI | Backend REST/WebSocket | rápido, tipado, Python/IA | baixo | alta | média |
| PostgreSQL | Banco principal | robusto, SQL, extensível | baixo/médio | alta | média |
| PostGIS | Geoespacial | padrão de mercado GIS | baixo | alta | média/alta |
| TimescaleDB | Séries temporais | compressão/agregações | baixo/médio | alta | média |
| Redis | Cache/filas curtas | simples e rápido | baixo | média/alta | baixa |
| EMQX | MQTT produção | cluster, ACL, observabilidade | médio | alta | média |
| Mosquitto | MQTT MVP | leve e simples | baixo | média | baixa |
| Docker | Containers | padroniza ambiente | baixo | alta | baixa/média |
| Kubernetes/K3s | Orquestração | escala e resiliência | médio/alto | muito alta | alta |
| GitHub Actions | CI/CD | integrado ao repo | baixo | alta | baixa/média |
| React Native/Expo | Mobile | base já existente, rápido MVP | baixo | alta | média |
| React/Next.js | Dashboard web | ecossistema forte | baixo | alta | média |
| Streamlit | Dashboard científico MVP | rápido para demo/data | baixo | média | baixa |
| YOLO/Ultralytics | Visão computacional | excelente detecção | baixo/médio | alta | média |
| OpenCV | Processamento imagem | maduro e flexível | baixo | alta | média |
| Roboflow | Dataset visual | anotação/gestão | médio | alta | baixa |
| MLflow | MLOps | registry/experimentos | baixo | alta | média |
| Sentinel Hub | Copernicus API | rápido e produtivo | médio | alta | média |
| Copernicus Data Space | Dados oficiais | amplo e aberto | baixo | alta | média/alta |
| ERA5/xarray | Clima | dados confiáveis | baixo | alta | alta |
| ESP32-S3 | Nó IoT | baixo custo e potente | baixo | alta | média |
| LoRa/LoRaWAN | Rural IoT | longo alcance | médio | alta | média |
| Grafana/Prometheus | Observabilidade | padrão cloud native | baixo | alta | média |
| S3/Cloud Storage | Objetos | imagens/rasters/modelos | baixo/médio | muito alta | baixa |
| Cloudflare | CDN/WAF/DNS | proteção e performance | baixo | alta | baixa |

---

# 17. Estrutura de Pastas do Projeto

```text
BeeSpace/
├── README.md
├── docs/
│   ├── PLANO_TECNICO_OPERACIONAL_BEESPACE.md
│   ├── architecture/
│   ├── api/
│   ├── firmware/
│   ├── scientific-validation/
│   └── adr/
├── backend/
│   ├── app/
│   ├── migrations/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── firmware/
│   ├── src/
│   ├── include/
│   ├── test/
│   ├── platformio.ini
│   └── docs/
├── ai/
│   ├── vision/
│   ├── anomaly/
│   ├── acoustic/
│   ├── models/
│   ├── notebooks/
│   └── mlops/
├── geospatial/
│   ├── copernicus/
│   ├── era5/
│   ├── sentinel5p/
│   ├── pipelines/
│   └── tests/
├── apps/
│   ├── mobile/
│   ├── web/
│   └── marketplace/
├── dashboards/
│   ├── streamlit/
│   └── esg-web/
├── infra/
│   ├── docker/
│   ├── k8s/
│   ├── terraform/
│   └── monitoring/
├── scripts/
├── datasets/
│   ├── README.md
│   ├── metadata/
│   └── samples/
└── pipelines/
    ├── iot_ingestion/
    ├── copernicus_etl/
    ├── ml_training/
    └── reporting/
```

---

# 18. Estratégia Científica e Validação

## 18.1 Validação dos dados

- Calibrar sensores em laboratório antes do campo.
- Registrar certificados ou medições de referência.
- Comparar temperatura/umidade com instrumento padrão.
- Calibrar peso com massas conhecidas.
- Validar contagem de abelhas por vídeo manual em amostras.
- Validar áudio com eventos conhecidos.

## 18.2 Protocolos experimentais

- Grupo controle sem intervenção e grupo monitorado.
- Múltiplas regiões e sazonalidades.
- Registro de manejo padronizado.
- Inspeção humana periódica com checklist.
- Eventos anotados: alimentação, colheita, doença, enxameação, pesticide suspicion.
- Separar dados de treino, validação e teste por colmeia/região para evitar vazamento.

## 18.3 Métricas científicas

- Precisão de sensor: erro médio, desvio padrão, drift.
- Alertas: precision, recall, F1, lead time e taxa de falso alarme.
- Visão: mAP, precision/recall por classe, matriz de confusão.
- Séries temporais: MAE/RMSE para previsão.
- ESG: rastreabilidade, repetibilidade e incerteza.

## 18.4 Artigos e rigor

- Publicar protocolo metodológico antes de claims comerciais fortes.
- Trabalhar com universidades, Embrapa, cooperativas ou laboratórios.
- Evitar causalidade indevida: usar linguagem de risco/indício quando apropriado.
- Documentar limitações por espécie, clima, região, sensor e modelo.

---

# 19. Estratégia de Monetização Tecnológica

## 19.1 Modelos de receita

- **SaaS por colmeia:** mensalidade por colmeia ativa.
- **Hardware as a Service:** aluguel do kit com manutenção.
- **Venda de hardware:** margem no kit e assinatura de dados.
- **API ambiental:** dados agregados e scores para agronegócio, seguradoras, pesquisa e governo.
- **Relatórios ESG:** relatórios auditáveis por fazenda/projeto.
- **Marketplace:** comissão sobre vendas de produtos/serviços apícolas.
- **Licenciamento:** tecnologia para cooperativas e programas públicos.
- **BeeCoin:** apenas como programa de incentivo/creditos internos no início; não priorizar cripto regulada no MVP.

## 19.2 Planos SaaS sugeridos

- **Starter:** até 5 colmeias, dashboard básico, alertas simples.
- **Pro:** até 50 colmeias, Copernicus, app, relatórios e visão computacional.
- **Business/ESG:** multiusuário, relatórios ESG, API, suporte e SLA.
- **Enterprise/B2G:** customização, integração, dados territoriais e implantação dedicada.

## 19.3 Modelo financeiro escalável

- Reduzir custo cloud por colmeia com edge aggregation.
- Cobrar por retenção longa, relatórios, imagens e API.
- Manter hardware modular para margem e manutenção.
- Usar dados agregados anonimizados para produtos B2B com consentimento.
- Separar receita recorrente SaaS da receita não recorrente de instalação/hardware.

---

# 20. Próximos Passos Prioritários

## 20.1 Ações imediatas

1. Criar `backend/` FastAPI mínimo com Docker Compose.
2. Definir schema oficial de payload IoT v1.
3. Criar PostgreSQL/PostGIS com tabelas `tenants`, `hives`, `devices`, `telemetry_raw`, `telemetry_snapshots`, `alerts`.
4. Integrar broker MQTT e endpoint HTTP fallback.
5. Adaptar firmware para publicar no contrato v1.
6. Conectar app mobile ao backend real.
7. Migrar pipeline Copernicus existente para job assíncrono.
8. Criar endpoint de upload/inferência visual.
9. Definir protocolo de piloto com 2-3 colmeias.
10. Implantar staging com CI/CD e observabilidade mínima.

## 20.2 Checklist operacional

- [ ] Payload versionado e documentado.
- [ ] Device credentials únicas.
- [ ] Banco PostGIS provisionado.
- [ ] Ingestão MQTT testada.
- [ ] Buffer offline no firmware.
- [ ] Dashboard com mapa e séries temporais.
- [ ] Copernicus real ou fallback.
- [ ] Alertas com evidências.
- [ ] App mobile com snapshot real.
- [ ] Pipeline YOLO executável.
- [ ] Logs e métricas.
- [ ] Backup básico.
- [ ] Política LGPD inicial.
- [ ] Protocolo científico inicial.

## 20.3 Prioridades técnicas

- Confiabilidade de ingestão.
- Baixo consumo energético.
- Contratos de dados estáveis.
- Observabilidade desde o MVP.
- PostGIS como base geoespacial.
- Modular monolith antes de microsserviços.

## 20.4 Prioridades científicas

- Calibração de sensores.
- Validação de alertas por inspeção humana.
- Dataset visual anotado com qualidade.
- Métricas de incerteza e explicabilidade.
- Separação entre correlação e causalidade.

## 20.5 Prioridades de negócio

- Piloto com produtores reais.
- Proposta de valor simples: reduzir perdas, melhorar manejo e gerar evidência ambiental.
- Relatórios ESG com metodologia transparente.
- Custo por colmeia competitivo.
- Parcerias com cooperativas, universidades e órgãos ambientais.
