1	<div align="center">
     2	
     3	# 🐝 BeeSpace: Biodiversidade em Órbita 🛰️
     4	
     5	**Colmeias inteligentes para monitorar biodiversidade, clima, produção apícola e sinais ambientais, conectando sensores de campo, visão computacional, ciência de dados geoespaciais e dados Copernicus.**
     6	
     7	**IoT · Machine Learning · Visão Computacional · Copernicus · ESG com dados verificáveis**
     8	
     9	</div>
    10	
    11	---
    12	
    13	## Bem-vindo à colmeia
    14	
    15	A **BeeSpace** transforma colmeias tradicionais em **biossensores inteligentes**. O projeto combina hardware embarcado, telemetria contínua, modelos de Machine Learning, visão computacional e dados orbitais para apoiar apicultores, pesquisadores, empresas e iniciativas de conservação.
    16	
    17	A proposta central é cruzar:
    18	
    19	- **Microdados da colmeia:** temperatura, umidade, peso, luminosidade, movimento, fluxo de abelhas, acústica e imagens de favos.
    20	- **Macrodados ambientais:** vegetação, relevo, clima, cobertura do solo, radar orbital e indicadores atmosféricos obtidos a partir de fontes como Copernicus, Sentinel e catálogos STAC.
    21	
    22	---
    23	
    24	## Sumário
    25	
    26	- [Sobre o projeto](#sobre-o-projeto)
    27	- [Por que abelhas?](#por-que-abelhas)
    28	- [Arquitetura do sistema](#arquitetura-do-sistema)
    29	- [Estrutura atual do repositório](#estrutura-atual-do-repositório)
    30	- [Módulos presentes](#módulos-presentes)
    31	- [Como executar cada parte](#como-executar-cada-parte)
    32	- [Hardware e firmware](#hardware-e-firmware)
    33	- [Ciência de dados geoespaciais](#ciência-de-dados-geoespaciais)
    34	- [Visão computacional](#visão-computacional)
    35	- [Aplicativo mobile](#aplicativo-mobile)
    36	- [Roadmap](#roadmap)
    37	- [Como contribuir](#como-contribuir)
    38	- [Licença](#licença)
    39	
    40	---
    41	
    42	## Sobre o projeto
    43	
    44	A BeeSpace nasceu de uma necessidade real do campo: monitorar colmeias de forma contínua, confiável, acessível e auditável. Para isso, o repositório reúne protótipos e experimentos em cinco frentes:
    45	
    46	| Frente | Papel no projeto |
    47	|---|---|
    48	| **Firmware ESP32-S3** | Coleta telemetria local, executa lógica embarcada e publica payloads MQTT/JSON. |
    49	| **IA e ML tabular** | Classifica risco ambiental, produtivo e sanitário a partir de dados sintéticos e telemetria. |
    50	| **Visão computacional** | Analisa fotos de favos com YOLO para medir composição visual: mel, néctar, pólen, ovos, larvas e crias. |
    51	| **JupyterLab geoespacial** | Processa dados Sentinel, DEM, SAR e fusão Geo-IoT para leitura territorial. |
    52	| **Aplicativo mobile** | Demonstra a experiência de manejo, métricas, alertas e visualização de dados da colmeia. |
    53	
    54	---
    55	
    56	## Por que abelhas?
    57	
    58	Abelhas são bioindicadores importantes porque dependem diretamente da qualidade do ambiente no entorno da colmeia. Uma colmeia saudável reflete disponibilidade de água, flora, baixa pressão química, microclima adequado, alimento e estabilidade ecológica.
    59	
    60	O monitoramento de colmeias permite observar sinais de alerta precoce relacionados a:
    61	
    62	- estresse térmico e hídrico;
    63	- perda de vegetação e redução de pasto apícola;
    64	- poluição atmosférica ou pressão química;
    65	- anomalias acústicas e comportamentais;
    66	- mortalidade observada;
    67	- alterações de peso e produtividade;
    68	- riscos de furto, impacto ou tombamento.
    69	
    70	---
    71	
    72	## Arquitetura do sistema
    73	
    74	```mermaid
    75	flowchart TD
    76	    A[Colmeia inteligente ESP32-S3] --> B[Firmware embarcado]
    77	    B --> C[Telemetria MQTT/JSON]
    78	    C --> D[Análise IA / Backend / Dashboards]
    79	    E[App mobile Expo] --> F[Manejo e leitura de métricas]
    80	    F --> D
    81	    G[Fotos de favos] --> H[YOLO / Visão computacional]
    82	    H --> D
    83	    I[Sentinel / Copernicus / DEM / STAC] --> J[JupyterLab geoespacial]
    84	    J --> D
    85	    D --> K[Alertas ambientais, produtivos e ESG]
    86	```
    87	
    88	Fluxo conceitual:
    89	
    90	1. A colmeia coleta sinais físicos, acústicos e ambientais.
    91	2. O firmware no ESP32-S3 organiza leituras de sensores e eventos.
    92	3. A telemetria é preparada para publicação em MQTT/JSON.
    93	4. Scripts Python e notebooks analisam risco, anomalias e contexto territorial.
    94	5. O app mobile apresenta uma experiência de manejo e acompanhamento.
    95	6. A visão computacional transforma imagens de favos em indicadores objetivos.
    96	
    97	---
    98	
    99	## Estrutura atual do repositório
   100	
   101	A árvore abaixo reflete os diretórios e arquivos presentes no repositório, ignorando `.git/` e `node_modules/`.
   102	
   103	```text
   104	BeeSpace/
   105	├── README.md
   106	├── hardware.png
   107	├── MVP-BeeSpace/
   108	│   ├── LICENSE
   109	│   ├── README.md
   110	│   ├── beespace_mvp.py
   111	│   ├── dados_sinteticos_beespace.xlsx
   112	│   ├── gitignore
   113	│   ├── modelo_beespace_mvp.pkl
   114	│   └── requirements.docx
   115	├── JupyterLab/
   116	│   ├── README.md
   117	│   ├── Análise-Topográfica-Microclimas(DEM)/
   118	│   │   ├── DEM.py
   119	│   │   └── REDME.md
   120	│   ├── Automação.Temporais(Sentinel-1.SAR)/
   121	│   │   ├── README.md
   122	│   │   └── sentinel1_stac_metadata.py
   123	│   ├── Fusão.Macro.Micro/
   124	│   │   ├── REDME.md
   125	│   │   └── beespace_geo_iot.py
   126	│   └── NDVI.Sentinel-2/
   127	│       ├── NDVI.Sentinel-2.py
   128	│       └── REDME.md
   129	├── apps/
   130	│   ├── mobile/
   131	│   │   ├── .gitignore
   132	│   │   ├── App.tsx
   133	│   │   ├── README.md
   134	│   │   ├── app.json
   135	│   │   ├── babel.config.js
   136	│   │   ├── package.json
   137	│   │   ├── tsconfig.json
   138	│   │   └── src/
   139	│   │       ├── components/
   140	│   │       │   ├── MetricTile.tsx
   141	│   │       │   ├── ProgressBar.tsx
   142	│   │       │   └── SectionCard.tsx
   143	│   │       ├── data/
   144	│   │       │   └── mockHive.ts
   145	│   │       ├── services/
   146	│   │       │   └── api.ts
   147	│   │       ├── theme.ts
   148	│   │       ├── types/
   149	│   │       │   └── beespace.ts
   150	│   │       └── utils/
   151	│   │           └── status.ts
   152	│   └── web/
   153	│       └── .gitkeep
   154	├── firmware/
   155	│   └── esp32-s3/
   156	│       ├── IA.py
   157	│       ├── README.md
   158	│       ├── main.cpp
   159	│       └── platformio.ini
   160	└── visao.computacional/
   161	    ├── COD.py
   162	    └── README.md
   163	```
   164	
   165	---
   166	
   167	## Módulos presentes
   168	
   169	| Caminho | Conteúdo | Status |
   170	|---|---|---|
   171	| `MVP-BeeSpace/` | MVP em Python com Random Forest, dados sintéticos em Excel, modelo `.pkl`, documentação e licença própria. | Prova de conceito de ML tabular. |
   172	| `firmware/esp32-s3/` | Projeto PlatformIO/Arduino para ESP32-S3, firmware principal e script Python de detecção de anomalias por Isolation Forest. | Protótipo embarcado e IA operacional externa ao microcontrolador. |
   173	| `visao.computacional/` | Pipeline Python para carregar YOLO, inferir classes em imagens de favos e gerar composição quantitativa. | Módulo de inferência para manejo visual. |
   174	| `JupyterLab/` | Hub de scripts e documentação para NDVI Sentinel-2, Sentinel-1 SAR, DEM e fusão Geo-IoT. | Experimentos de ciência de dados espaciais. |
   175	| `apps/mobile/` | Aplicativo React Native/Expo com tela demonstrativa, dados mockados, componentes, tipos e utilitários. | Protótipo mobile. |
   176	| `apps/web/` | Diretório reservado com `.gitkeep`. | Placeholder para futura aplicação web. |
   177	| `hardware.png` | Ilustração da arquitetura física da colmeia inteligente. | Ativo visual de documentação. |
   178	
   179	---
   180	
   181	## Como executar cada parte
   182	
   183	### MVP de Machine Learning tabular
   184	
   185	```bash
   186	cd MVP-BeeSpace
   187	python beespace_mvp.py
   188	```
   189	
   190	O script gera dados sintéticos, treina um classificador, avalia o desempenho, calcula importância de variáveis, simula uma nova colmeia e salva artefatos como dataset e modelo.
   191	
   192	> Observação: o diretório possui `requirements.docx`, mas não possui `requirements.txt`. Instale manualmente as dependências Python usadas no script, como `numpy`, `pandas`, `scikit-learn`, `joblib` e bibliotecas de planilha necessárias ao seu ambiente.
   193	
   194	### Firmware ESP32-S3
   195	
   196	```bash
   197	cd firmware/esp32-s3
   198	pio run
   199	```
   200	
   201	Para gravar em uma placa conectada:
   202	
   203	```bash
   204	pio run --target upload
   205	```
   206	
   207	Para abrir o monitor serial:
   208	
   209	```bash
   210	pio device monitor
   211	```
   212	
   213	O projeto usa PlatformIO com framework Arduino para `esp32-s3-devkitc-1`.
   214	
   215	### IA de anomalias da telemetria
   216	
   217	```bash
   218	python firmware/esp32-s3/IA.py
   219	```
   220	
   221	Esse script roda em computador, gateway, servidor ou backend. Ele não é firmware do ESP32-S3; ele treina e exporta um modelo `modelo_beespace_isolation_forest.pkl` para analisar telemetria da colmeia.
   222	
   223	### Visão computacional
   224	
   225	```bash
   226	python visao.computacional/COD.py --model best.pt --image exemplos/favo.jpg --output-dir saidas
   227	```
   228	
   229	O comando espera um peso YOLO treinado, por exemplo `best.pt`, e uma imagem de favo. O módulo foi estruturado para contar classes e gerar indicadores percentuais.
   230	
   231	### JupyterLab geoespacial
   232	
   233	```bash
   234	python -m venv .venv
   235	source .venv/bin/activate
   236	python -m pip install --upgrade pip setuptools wheel
   237	python -m pip install jupyterlab numpy pandas geopandas shapely rasterio folium matplotlib pystac-client requests
   238	jupyter lab JupyterLab/
   239	```
   240	
   241	Módulos disponíveis:
   242	
   243	- `JupyterLab/NDVI.Sentinel-2/` — cálculo e visualização de NDVI.
   244	- `JupyterLab/Automação.Temporais(Sentinel-1.SAR)/` — consulta de metadados Sentinel-1 em catálogo STAC.
   245	- `JupyterLab/Análise-Topográfica-Microclimas(DEM)/` — análise de elevação, declividade e microclimas.
   246	- `JupyterLab/Fusão.Macro.Micro/` — fusão entre telemetria IoT e camadas geoespaciais.
   247	
   248	### Aplicativo mobile
   249	
   250	```bash
   251	cd apps/mobile
   252	npm install
   253	npm run start
   254	```
   255	
   256	Comandos adicionais:
   257	
   258	```bash
   259	npm run android
   260	npm run ios
260	npm run ios
   261	npm run web
   262	npm run typecheck
   263	```
   264	
   265	O app usa Expo, React Native e TypeScript. A versão atual trabalha com dados mockados e componentes reutilizáveis para métricas e status da colmeia.
   266	
   267	---
   268	
   269	## Hardware e firmware
   270	
   271	![Hardware da BeeSpace](hardware.png)
   272	
   273	<details>
   274	  <summary><strong>Descrição da imagem</strong></summary>
   275	
   276	Ilustração de uma colmeia instrumentada com painel solar, ESP32-S3, sensores de temperatura e umidade, microfone, catracas ópticas, célula de carga, acelerômetro e comunicação sem fio com a nuvem BeeSpace.
   277	
   278	</details>
   279	
   280	Componentes representados na proposta:
   281	
   282	- **ESP32-S3** como unidade de processamento embarcado.
   283	- **BME280** para temperatura, umidade e pressão.
   284	- **INMP441** para assinatura acústica via I2S.
   285	- **TCRT5000** para contagem de entrada e saída de abelhas.
   286	- **HX711 + células de carga** para peso da colmeia.
   287	- **MPU6050** para impacto, vibração e possível furto.
   288	- **BH1750** para luminosidade.
   289	- **Bateria 18650, carregamento e painel solar** para autonomia.
   290	
   291	---
   292	
   293	## Ciência de dados geoespaciais
   294	
   295	A camada `JupyterLab/` complementa a telemetria local com observação da Terra:
   296	
   297	- **Sentinel-2 / NDVI:** vigor da vegetação e disponibilidade de pasto apícola.
   298	- **Sentinel-1 SAR:** leitura por radar em cenários com nuvens, fumaça ou baixa luminosidade.
   299	- **Copernicus DEM:** relevo, altitude, declividade e influência topográfica em microclimas.
   300	- **Fusão Geo-IoT:** integração de sinais da colmeia com camadas espaciais e mapas interativos.
   301	
   302	Essa camada ajuda a responder se uma alteração observada na colmeia é local, ambiental, climática ou territorial.
   303	
   304	---
   305	
   306	## Visão computacional
   307	
   308	O módulo `visao.computacional/` organiza o pipeline para análise de imagens de favos com YOLO. As classes esperadas no domínio BeeSpace são:
   309	
   310	- `mel`
   311	- `nectar`
   312	- `polen`
   313	- `ovos`
   314	- `larvas`
   315	- `crias_operculadas`
   316	
   317	A meta é reduzir subjetividade no manejo, transformando inspeções visuais em contagens, percentuais, relatórios e imagens anotadas.
   318	
   319	---
   320	
   321	## Aplicativo mobile
   322	
   323	O app em `apps/mobile/` é um protótipo Expo/React Native para apresentar a BeeSpace ao usuário de campo. Ele reúne:
   324	
   325	- tela principal em `App.tsx`;
   326	- componentes de cartão, métricas e barras de progresso;
   327	- tema visual centralizado;
   328	- dados mockados de colmeia;
   329	- tipos TypeScript do domínio;
   330	- serviço de API preparado para futura integração.
   331	
   332	---
   333	
   334	## Roadmap
   335	
   336	Próximas evoluções sugeridas, considerando a estrutura atual do repositório:
   337	
   338	- Padronizar nomes `REDME.md` para `README.md` nos submódulos em que isso ainda aparece.
   339	- Criar `requirements.txt` ou `pyproject.toml` para os módulos Python.
   340	- Definir contratos MQTT/JSON versionados.
   341	- Separar credenciais do firmware em provisionamento seguro ou NVS.
   342	- Adicionar testes automatizados para Python e TypeScript.
   343	- Documentar esquemáticos eletrônicos e lista de materiais em um diretório dedicado.
   344	- Evoluir `apps/web/` de placeholder para dashboard web.
   345	- Integrar o app mobile a uma API real de telemetria.
   346	
   347	---
   348	
   349	## Como contribuir
   350	
   351	Contribuições são bem-vindas para fortalecer a colmeia:
   352	
   353	1. Faça um fork do repositório.
   354	2. Crie uma branch com nome descritivo.
   355	3. Documente alterações de hardware, firmware, dados, modelos ou interface.
   356	4. Inclua exemplos mínimos reproduzíveis quando possível.
   357	5. Abra um Pull Request explicando impacto, testes e limitações.
   358	
   359	Áreas prioritárias:
   360	
   361	- firmware ESP32-S3;
   362	- modelos YOLO;
   363	- integração Copernicus/STAC;
   364	- dashboards e app mobile;
   365	- validação científica e documentação.
   366	
   367	---
   368	
   369	## Licença
   370	
   371	O diretório `MVP-BeeSpace/` possui arquivo `LICENSE`. Para o restante do repositório, a licença geral ainda deve ser formalizada. Até a publicação de uma licença raiz, trate o conteúdo fora de `MVP-BeeSpace/` como material do projeto BeeSpace com direitos reservados.
   372	
   373	---
   374	
   375	<div align="center">
   376	
   377	**BeeSpace — biodiversidade monitorada por colmeias, dados e órbita.**
   378	
   379	🐝 + 🛰️ + 💻 + 🌱
   380	
   381	</div>
