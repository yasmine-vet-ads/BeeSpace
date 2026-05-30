diff --git a/README.md b/README.md
index 3f936b6cade3291d0e46ab5fb7c66ca28c35ff5d..547072bce483ca82b823c7eb3cfc08db52450267 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,398 @@
-# BeeSpace
\ No newline at end of file
+<div align="center">
+
+# 🐝 BeeSpace: Biodiversidade em Órbita 🛰️
+
+**Colmeias inteligentes para monitorar biodiversidade, clima, produção apícola e sinais ambientais — do micro da colmeia ao macro dos satélites Copernicus.**
+
+< **IoT** | **Machine Learning** | **Visão Computacional** | **Copernicus** | **ESG com dados verificáveis** >
+
+</div>
+
+---
+
+> Bem-vindo à colmeia
+
+=> Seja bem-vindo à nossa colmeia e obrigado pelo interesse em conhecer a **BeeSpace**.
+
+| A BeeSpace transforma colmeias tradicionais em **biossensores inteligentes**, combinando hardware embarcado, telemetria contínua, modelos de visão computacional e dados orbitais para apoiar apicultores, pesquisadores, empresas e iniciativas ESG.
+
+[ Cultura maker ] [ Ciência aplicada ] [ Impacto ambiental ] [ Dados confiáveis ]
+
+---
+
+> Sumário
+
+=> [Sobre o projeto](#sobre-o-projeto)
+=> [Por que abelhas?](#por-que-abelhas)
+=> [Arquitetura do sistema](#arquitetura-do-sistema)
+=> [Estrutura do repositório](#estrutura-do-repositório)
+=> [Hardware e colmeia inteligente](#hardware-e-colmeia-inteligente)
+=> [Firmware e edge computing](#firmware-e-edge-computing)
+=> [Visão computacional no manejo](#visão-computacional-no-manejo)
+=> [Dados Copernicus: do micro ao macro](#dados-copernicus-do-micro-ao-macro)
+=> [Missão 2030](#missão-2030)
+=> [Enxame BeeSpace](#enxame-beespace)
+=> [Roadmap](#roadmap)
+=> [Como contribuir](#como-contribuir)
+=> [Licença](#licença)
+
+---
+
+## > Sobre o projeto
+
+=> **BeeSpace** nasce de uma necessidade real relatada por apicultores: a dificuldade de monitorar colmeias de forma contínua, confiável e economicamente acessível.
+
+=> Para resolver esse desafio, unimos:
+
+[ Inspeção de produtos de origem animal ]
+[ Entomologia ]
+[ Engenharia de Software ]
+[ Ciência de Dados ]
+[ Machine Learning ]
+[ Visão Computacional ]
+[ Sistemas Embarcados ]
+[ Dados orbitais Copernicus ]
+
+| A proposta é transformar cada colmeia em uma **mini estação meteorológica e biológica**, capaz de emitir sinais de alerta precoce sobre alterações ambientais, estresse, mortalidade, desmatamento, poluição e possíveis impactos de agrotóxicos.
+
+=> O diferencial está na união entre:
+
+\# **Micro**: dados clínicos da colmeia, como padrões acústicos, temperatura, umidade, peso, luminosidade, movimento, fluxo de entrada e saída de abelhas.
+\# **Macro**: dados de satélite, vegetação, fenologia, clima e qualidade do ar obtidos por Copernicus, Sentinel Hub API e Copernicus Data Space.
+
+---
+
+## > Por que abelhas?
+
+=> **Bioindicopowers** 🦸‍♀️
+
+As abelhas são bioindicadores extraordinários. Elas voam, em média, em um raio de **3 km** a partir da colmeia, cobrindo uma área aproximada de **2.827 hectares**.
+
+=> Em sua anatomia, possuem corpos com **pelos ramificados**. Durante o voo, a energia estática produzida faz com que esses pelos funcionem como verdadeiros **ímãs naturais**, coletando materiais particulados presentes no ar.
+
+=> Uma colmeia saudável depende de:
+
+\# água disponível;
+\# fauna e flora equilibradas;
+\# baixa pressão química;
+\# temperatura e umidade adequadas;
+\# disponibilidade de pasto apícola;
+\# ausência de eventos ambientais extremos.
+
+| Sem as abelhas, ecossistemas inteiros entrariam em colapso. Elas atuam como polinizadoras de quase **90% das plantas com flores silvestres** e cerca de **75% das culturas alimentares**.
+
+---
+
+## > Arquitetura do sistema
+
+=> A BeeSpace é organizada em camadas integradas:
+
+```mermaid
+flowchart TD
+    A[Colmeia Inteligente ESP32-S3] --> B[Edge Computing FreeRTOS]
+    B --> C[MQTT + JSON]
+    C --> D[Cloud / APIs / Dashboards]
+    D --> E[Alertas ESG e Biodiversidade]
+    F[App de Manejo] --> G[Imagens da Colmeia]
+    G --> H[YOLO / Visão Computacional]
+    H --> D
+    I[Copernicus / Sentinel Hub] --> J[NDVI, ERA5, CAMS, HR-VPP]
+    J --> D
+```
+
+=> Fluxo principal:
+
+\# A colmeia coleta sinais físicos, acústicos e ambientais.
+\# O firmware processa eventos em borda usando **FreeRTOS**.
+\# Os dados são publicados em **MQTT/JSON**.
+\# A plataforma cruza telemetria da colmeia com imagens e dados orbitais.
+\# Alertas são gerados para apicultores, pesquisadores e parceiros ESG.
+
+---
+
+## > Estrutura do repositório
+
+=> Organização recomendada para o repositório principal da BeeSpace:
+
+```text
+BeeSpace/
+├── README.md
+├── apps/
+│   ├── mobile/
+│   └── web/
+├── cloud/
+│   ├── dashboard/
+│   ├── infra/
+│   └── mqtt/
+├── computer_vision/
+│   ├── datasets/
+│   ├── inference/
+│   ├── models/
+│   ├── notebooks/
+│   └── training/
+├── copernicus_api/
+│   ├── configs/
+│   ├── notebooks/
+│   ├── src/
+│   └── tests/
+├── data/
+│   ├── processed/
+│   ├── raw/
+│   └── samples/
+├── docs/
+│   ├── architecture/
+│   ├── devrel/
+│   └── research/
+├── firmware/
+│   └── esp32-s3/
+│       ├── include/
+│       ├── lib/
+│       ├── src/
+│       └── test/
+├── hardware/
+│   ├── bom/
+│   ├── enclosure/
+│   └── schematics/
+└── scripts/
+```
+
+=> Responsabilidades por diretório:
+
+[ `hardware/` ] esquemáticos, listas de materiais, caixa, sensores, alimentação e prototipagem.
+[ `firmware/` ] código embarcado para ESP32-S3, FreeRTOS, sensores, MQTT e energia.
+[ `computer_vision/` ] datasets, treinamento YOLO, inferência, modelos e notebooks.
+[ `copernicus_api/` ] integrações com Sentinel Hub API, Copernicus Data Space, ERA5, CAMS e HR-VPP.
+[ `cloud/` ] broker MQTT, dashboards, infraestrutura e serviços de ingestão.
+[ `apps/` ] aplicativos mobile e web para manejo, visualização e alertas.
+[ `data/` ] dados brutos, processados e amostras públicas ou sintéticas.
+[ `docs/` ] arquitetura, pesquisa, materiais DevRel e documentação científica.
+[ `scripts/` ] automações para setup, coleta, treinamento e publicação.
+
+---
+
+## > Hardware e colmeia inteligente
+
+=> **Edge Computing & Dados Orbitais**
+
+O hardware embarcado de baixo custo atua como o **sistema nervoso da colmeia**, capturando sinais críticos para interpretar saúde, produtividade e risco ambiental.
+
+### > Hardware e sensores conectados
+
+[ INMP441 ] **Microfone I2S** para assinatura acústica da colmeia.
+[ BME280 ] **I2C** para temperatura e umidade interna.
+[ TCRT5000 ] **Pinos digitais** para catracas ópticas com interrupções.
+[ HX711 + 4 células de carga ] balança de mel e variação de massa da colmeia.
+[ MPU6050 ] **I2C** para acelerômetro antifurto e detecção de vibrações.
+[ BH1750 ] **I2C** para luminosidade externa.
+[ Divisor de tensão ] **ADC** para nível da bateria 18650 e mini painel solar.
+
+=> Exemplo de ponto de entrada para firmware:
+
+```cpp
+// firmware/esp32-s3/src/CodeHardware.cpp
+// TODO: inicializar barramentos I2C, I2S, ADC e GPIO.
+// TODO: registrar tasks FreeRTOS para sensores, energia e MQTT.
+// TODO: publicar payload JSON com telemetria da colmeia.
+
+void setupBeeSpaceHardware() {
+  // Preencher com inicialização dos sensores BeeSpace.
+}
+
+void loopBeeSpaceHardware() {
+  // Preencher com ciclo de leitura, inferência local e publicação MQTT.
+}
+```
+
+---
+
+## > Firmware e edge computing
+
+=> Arquitetura de software embarcado:
+
+[ FreeRTOS ] tasks independentes para sensores, comunicação, áudio e energia.
+[ MQTT/JSON ] telemetria padronizada para ingestão em nuvem.
+[ Deep Sleep ] gerenciamento de energia no **ESP32-S3**.
+[ Interrupções ] contagem de entrada e saída de abelhas com catracas ópticas.
+[ Edge Processing ] pré-processamento local para reduzir consumo e tráfego.
+
+=> Bibliotecas previstas:
+
+\# `Adafruit_BME280`
+\# `HX711`
+\# `PubSubClient`
+\# `driver/i2s.h`
+
+=> Exemplo de payload MQTT:
+
+```json
+{
+  "device_id": "beespace-hive-0001",
+  "timestamp": "2026-05-30T00:00:00Z",
+  "sensors": {
+    "temperature_c": 34.8,
+    "humidity_percent": 61.2,
+    "weight_kg": 42.5,
+    "battery_v": 3.91,
+    "light_lux": 1800,
+    "bee_in_count": 128,
+    "bee_out_count": 119,
+    "motion_alert": false
+  },
+  "audio": {
+    "signature_status": "normal",
+    "stress_score": 0.12
+  }
+}
+```
+
+---
+
+## > Visão computacional no manejo
+
+=> A BeeSpace leva modelos de **Machine Learning** diretamente para o manejo presencial.
+
+\# O produtor registra fotos pelo aplicativo.
+\# A base de imagens é anotada no **Roboflow**.
+\# O treinamento utiliza arquitetura **YOLO — You Only Look Once**.
+\# A plataforma processa fotos instantaneamente.
+\# As detecções são convertidas em gráfico dinâmico percentual.
+
+=> Classes de interesse nos alvéolos:
+
+[ Mel ] [ Néctar ] [ Pólen ] [ Ovos ] [ Larvas ] [ Crias ]
+
+| O objetivo é eliminar a subjetividade humana no manejo, fornecendo indicadores visuais padronizados, auditáveis e comparáveis ao longo do tempo.
+
+=> Exemplo de estrutura para inferência:
+
+```python
+\# computer_vision/inference/predict_frames.py
+\# TODO: carregar modelo YOLO treinado.
+\# TODO: receber imagem enviada pelo app.
+\# TODO: retornar classes, bounding boxes e percentuais por quadro.
+
+def predict_hive_frame(image_path: str) -> dict:
+    return {
+        "honey": 0.0,
+        "nectar": 0.0,
+        "pollen": 0.0,
+        "eggs": 0.0,
+        "larvae": 0.0,
+        "brood": 0.0,
+    }
+```
+
+---
+
+## > Dados Copernicus: do micro ao macro
+
+=> Monitoramos um raio de **3 km** ao redor da colmeia, equivalente a aproximadamente **28,27 km²**, usando **Sentinel Hub API** e **Copernicus Data Space**.
+
+[ Sentinel-2 ] **NDVI** para vigor da vegetação e pasto apícola.
+[ HR-VPP ] fenologia e produtividade da safra.
+[ Sentinel-5P / CAMS ] qualidade do ar e poluição cruzada com anomalias da colmeia.
+[ C3S / ERA5 ] dados climáticos para validação dos sensores físicos.
+
+=> A Verdade do Campo 🔍
+
+| A colmeia garante veracidade aos dados do campo porque seus sinais clínicos — padrões acústicos, estresse, mortalidade, temperatura, umidade e fluxo de abelhas — podem validar ou questionar leituras remotas.
+
+=> Aplicações diretas:
+
+\# detectar risco de desmatamento;
+\# identificar anomalias de vegetação;
+\# cruzar poluição atmosférica com estresse na colmeia;
+\# validar sensores físicos com ERA5;
+\# gerar alertas de biodiversidade;
+\# reduzir greenwashing com telemetria ininterrupta.
+
+=> Exemplo de função para integração orbital:
+
+```python
+\# copernicus_api/src/fetch_ndvi.py
+\# TODO: autenticar no Sentinel Hub ou Copernicus Data Space.
+\# TODO: buscar imagens Sentinel-2 no raio de 3 km da colmeia.
+\# TODO: calcular NDVI e retornar séries temporais.
+
+def fetch_hive_ndvi(latitude: float, longitude: float, radius_km: float = 3.0) -> dict:
+    return {
+        "latitude": latitude,
+        "longitude": longitude,
+        "radius_km": radius_km,
+        "ndvi_series": []
+    }
+```
+
+---
+
+## > Missão 2030
+
+=> A BeeSpace é alinhada aos **Objetivos de Desenvolvimento Sustentável da ONU**:
+
+[ ODS 2 ] **Fome Zero e Agricultura Sustentável** — apoio à produtividade apícola e polinização.
+[ ODS 9 ] **Indústria, Inovação e Infraestrutura** — hardware aberto, IoT e dados aplicados.
+[ ODS 13 ] **Ação Contra a Mudança Global do Clima** — monitoramento climático e alertas ambientais.
+[ ODS 15 ] **Vida Terrestre** — biodiversidade, ecossistemas e conservação.
+
+< Meta: construir uma rede distribuída de colmeias inteligentes para monitorar biodiversidade em escala territorial até 2030. >
+
+---
+
+## > Enxame BeeSpace
+
+=> Nosso enxame une campo, ciência, dados e engenharia.
+
+[ Yasmine Santos ] **Diretora Executiva** — Médica Veterinária e ADS. **Abelha-integradora**.
+[ Marciano Bernardi ] **Diretor de Operações** — Administrador e produtor. **Abelha-campeira**.
+[ Marcos Corino ] **Diretor de Tecnologia** — Especialista em IoT. **Abelha-construtora**.
+[ Roger Silva ] **Diretor de Dados** — Eng. de Computação/ML. **Abelha-batedora**.
+[ Victor Mattos ] **Diretor de Desenvolvimento** — ADS/Robótica. **Abelha-arquiteta**.
+[ Eduarda Marini ] **Diretora Científica** — Bióloga. **Abelha-guardiã**.
+
+---
+
+## > Roadmap
+
+=> Próximas entregas técnicas:
+
+\# Documentar esquemáticos e BOM em `hardware/`.
+\# Criar firmware inicial para ESP32-S3 em `firmware/esp32-s3/`.
+\# Definir contrato MQTT/JSON oficial.
+\# Estruturar dataset e pipeline YOLO em `computer_vision/`.
+\# Criar cliente de integração Copernicus em `copernicus_api/`.
+\# Publicar dashboards de telemetria em `cloud/dashboard/`.
+\# Criar documentação técnica e científica em `docs/`.
+
+---
+
+## > Como contribuir
+
+=> Contribuições são bem-vindas para fortalecer a colmeia.
+
+\# Faça um fork do repositório.
+\# Crie uma branch com nome descritivo.
+\# Documente alterações de hardware, firmware, dados ou modelos.
+\# Inclua exemplos mínimos reproduzíveis quando possível.
+\# Abra um Pull Request explicando impacto, testes e limitações.
+
+=> Áreas prioritárias:
+
+[ Firmware ESP32-S3 ] [ Modelos YOLO ] [ Integração Copernicus ] [ Dashboards ] [ Documentação ] [ Validação científica ]
+
+---
+
+## > Licença
+
+=> Licença ainda em definição.
+
+| Enquanto a licença oficial não for publicada, considere o conteúdo como **todos os direitos reservados** ao projeto BeeSpace.
+
+---
+
+<div align="center">
+
+< **BeeSpace** — biodiversidade monitorada por colmeias, dados e órbita. >
+
+🐝 + 🛰️ + 💻 + 🌱
+
+</div>
