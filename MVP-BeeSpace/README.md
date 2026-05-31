<h1 align="center">🐝 BeeSpace ML MVP</h1>

<p align="center">
  <strong>Classificação inteligente de risco ambiental, produtivo e sanitário em colmeias conectadas</strong><br />
  <em>Prova de conceito do projeto BeeSpace no CopernicusLAC Panamá Hackathon 2026</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge" alt="Status do Projeto: MVP" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/scikit--learn-Random%20Forest-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="Scikit-Learn Random Forest" />
  <img src="https://img.shields.io/badge/Pandas-Data%20Pipeline-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/CopernicusLAC-Panam%C3%A1%202026-0B5CAD?style=for-the-badge" alt="CopernicusLAC Panamá Hackathon 2026" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License" />
</p>

---

A BeeSpace conecta **sensores de colmeias**, **dados geoespaciais**, **clima**, **visão computacional**, **bioacústica** e **observação da Terra** para transformar colmeias inteligentes em **biossensores territoriais** capazes de apoiar tomada de decisão e biovigilância ambiental.

---

## 📚 Tabela de Conteúdos

- [🚀 Sobre o Projeto](#-sobre-o-projeto)
- [🎯 Objetivo do MVP](#-objetivo-do-mvp)
- [📊 Fontes de Dados Previstas](#-fontes-de-dados-previstas)
- [⚙️ Como o Modelo Funciona](#️-como-o-modelo-funciona)
- [🧠 Modelo Utilizado](#-modelo-utilizado)
- [🗂️ Estrutura Sugerida do Repositório](#️-estrutura-sugerida-do-repositório)
- [📋 Requisitos](#-requisitos)
- [🛠️ Instalação](#️-instalação)
- [📦 Arquivo `requirements.txt`](#-arquivo-requirementstxt)
- [▶️ Execução](#️-execução)
- [🖥️ Saídas Esperadas](#️-saídas-esperadas)
- [🔎 Exemplo de Interpretação](#-exemplo-de-interpretação)
- [⚠️ Limitações do MVP](#️-limitações-do-mvp)
- [🧭 Próximos Passos](#-próximos-passos)
- [🧪 Possível Evolução Técnica](#-possível-evolução-técnica)
- [🌎 Aplicação no Projeto BeeSpace](#-aplicação-no-projeto-beespace)
- [📌 Aviso Sobre os Dados](#-aviso-sobre-os-dados)
- [📄 Licença](#-licença)
- [👥 Autoria](#-autoria)

---

## 🚀 Sobre o Projeto

A **BeeSpace** propõe transformar colmeias inteligentes em **biossensores territoriais**, conectando dados locais das colmeias com dados geoespaciais e climáticos do programa **Copernicus**.

A solução busca apoiar **produtores**, **pesquisadores**, **empresas parceiras** e **iniciativas de proteção da biodiversidade** por meio de indicadores baseados em:

| Pilar | Papel no projeto |
| :--- | :--- |
| **Dados de campo** | Registros observacionais e validação territorial |
| **Sensores IoT** | Monitoramento contínuo de temperatura, umidade, peso e eventos internos |
| **Visão computacional** | Análise de atividade, fluxo e mortalidade de abelhas |
| **Bioacústica** | Identificação de padrões sonoros e anomalias da colmeia |
| **Observação da Terra** | Integração com dados Copernicus, vegetação, clima, uso do solo e atmosfera |

Neste MVP, o objetivo é demonstrar como dados **macroambientais** e **microambientais** podem ser integrados em um pipeline de **Machine Learning** para classificar o estado de uma colmeia monitorada.

---

## 🎯 Objetivo do MVP
O script classifica cada **colmeia inteligente** em uma das seguintes classes:

| Classe | Significado |
| :--- | :--- |
| `normal` | Colmeia e entorno em condição favorável |
| `atencao` | Sinais moderados de risco ambiental, climático, produtivo ou sanitário |
| `alerta` | Combinação crítica de fatores ambientais e sinais anômalos da colmeia |
> ### 🧭 Missão / Lógica Central da BeeSpace
>
> **Dados Copernicus + sensores da colmeia + inteligência de dados = alerta acionável para biovigilância ambiental.**

---
## 📊 Fontes de Dados Previstas

Este MVP utiliza **dados sintéticos**, mas foi modelado considerando as fontes reais previstas na arquitetura da **BeeSpace**.

### 🛰️ Dados Copernicus e Ambientais

| Variável | Fonte prevista | Interpretação |
| :--- | :--- | :--- |
| `ndvi` | Sentinel-2 / CLMS | Vigor da vegetação |
| `evi` | Sentinel-2 | Densidade e atividade vegetal |
| `ndwi` | Sentinel-2 | Umidade da vegetação |
| `temp_media` | C3S / ERA5-Land | Temperatura média da área |
| `precipitacao_7d` | C3S / ERA5-Land | Chuva acumulada nos últimos 7 dias |
| `umidade_solo` | C3S / ERA5-Land | Condição hídrica do solo |
| `poluicao_indice` | Sentinel-5P / CAMS | Indicador de poluição atmosférica |
| `perc_mata_nativa` | CLMS Land Cover | Proporção de vegetação nativa no entorno |
| `perc_agricultura` | CLMS Land Cover | Proporção de agricultura ou monocultura |
| `perc_solo_exposto` | CLMS Land Cover | Proporção de solo exposto |

### 🐝 Dados da colmeia inteligente

| Variável | Fonte prevista | Interpretação |
| :--- | :--- | :--- |
| `temp_colmeia` | Sensor interno | Temperatura interna da colmeia |
| `umidade_colmeia` | Sensor interno | Umidade interna da colmeia |
| `variacao_peso_7d` | Célula de carga | Ganho ou perda de peso em 7 dias |
| `atividade_abelhas` | Visão computacional | Fluxo de entrada e saída de abelhas |
| `anomalia_acustica` | Bioacústica | Sinais sonoros anômalos |
| `mortalidade_observada` | Visão computacional ou registro de campo | Presença de mortalidade observada |

---
## ⚙️ Como o Modelo Funciona

O script executa as seguintes etapas:

| Etapa | Descrição |
| :---: | :--- |
| 1 | Gera uma base sintética com variáveis ambientais, territoriais e da colmeia. |
| 2 | Cria uma regra inicial de rotulagem para simular as classes `normal`, `atencao` e `alerta`. |
| 3 | Treina um modelo de classificação usando **Random Forest**. |
| 4 | Avalia o desempenho com **matriz de confusão** e **relatório de classificação**. |
| 5 | Calcula a **importância das variáveis** para apoiar a explicabilidade. |
| 6 | Simula a previsão de risco para uma nova colmeia. |
| 7 | Salva o modelo treinado e a base sintética em arquivos locais. |

---

## 🧠 Modelo Utilizado

O MVP utiliza o algoritmo **`RandomForestClassifier`**, da biblioteca **scikit-learn**.

A escolha do **Random Forest** se justifica porque ele:

| Justificativa | Benefício para o MVP |
| :--- | :--- |
| Funciona bem com dados tabulares | Adequado para variáveis ambientais, climáticas, territoriais e de sensores |
| Combina variáveis ambientais, climáticas e de sensores | Permite integrar macrocontexto territorial com sinais internos da colmeia |
| Permite capturar relações não lineares | Ajuda a representar interações complexas entre ambiente e saúde da colmeia |
| É robusto para uma prova de conceito | Reduz complexidade de modelagem em contexto de hackathon |
| Permite analisar a importância das variáveis | Apoia explicabilidade e comunicação técnica |
| É mais fácil de explicar em um contexto de hackathon | Facilita demonstração para bancas, parceiros e stakeholders |

---

## 🗂️ Estrutura Sugerida do Repositório

```text
beespace-ml-mvp/
├── README.md
├── beespace_mvp.py
├── requirements.txt
├── dados_sinteticos_beespace.csv
└── modelo_beespace_mvp.pkl
```

---
## 📋 Requisitos

## 🛠️ Instalação

Clone o repositório:

```bash

git clone https://github.com/seu-usuario/beespace-ml-mvp.git
cd beespace-ml-mvp
```

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual.

No **Windows**:

```bash
venv\Scripts\activate
```

No **Linux** ou **macOS**:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 📦 Arquivo `requirements.txt`

Caso ainda não exista, crie um arquivo `requirements.txt` com o seguinte conteúdo:

```text
numpy
pandas
scikit-learn
joblib
```

---

## ▶️ Execução

Execute o script principal:

```bash
python beespace_mvp.py
```

Ao final da execução, o script deverá:

| Resultado | Descrição |
| :--- | :--- |
| Base sintética | Gerar uma base sintética com variáveis ambientais e da colmeia |
| Treinamento | Treinar o modelo de classificação |
| Métricas | Exibir métricas de avaliação |
| Importância das variáveis | Listar as variáveis mais importantes |
| Simulação | Simular a classificação de uma nova colmeia |
| Modelo treinado | Salvar o modelo treinado em arquivo local |
| CSV sintético | Salvar a base sintética em CSV |

---

## 🖥️ Saídas Esperadas

O terminal exibirá informações como:

```text
Amostra dos dados
Distribuição das classes
Matriz de confusão
Relatório de classificação
Variáveis mais importantes para o modelo
Classe prevista
```

Também serão gerados dois arquivos:

| Arquivo | Finalidade |
| :--- | :--- |
| `modelo_beespace_mvp.pkl` | Modelo treinado salvo localmente |
| `dados_sinteticos_beespace.csv` | Base sintética usada no MVP |

---

## 🔎 Exemplo de Interpretação

Uma colmeia pode ser classificada como **`alerta`** quando ocorre uma combinação de fatores como:

| Fator | Sinal de risco |
| :--- | :--- |
| Vegetação | Baixo `ndvi` |
| Umidade da vegetação | Baixo `ndwi` ou baixa umidade da vegetação |
| Chuva recente | Pouca chuva recente |
| Clima | Alta temperatura média |
| Cobertura nativa | Baixa presença de mata nativa |
| Uso do solo | Predominância agrícola |
| Produção | Queda de peso da colmeia |
| Atividade | Baixa atividade das abelhas |
| Bioacústica | Anomalia acústica |
| Sanidade | Mortalidade observada |

> Essa lógica representa a proposta central da **BeeSpace**: o **satélite indica o contexto territorial**, enquanto a **colmeia valida o que está acontecendo no campo**.

---

## ⚠️ Limitações do MVP

> Este MVP é uma **prova de conceito** e possui limitações importantes.

| Limitação | Impacto |
| :--- | :--- |
| Os dados utilizados são sintéticos | Não representam medições reais de colmeias ou ambiente |
| Os rótulos das classes são gerados por regras simuladas | A classificação ainda depende de lógica artificial inicial |
| O modelo ainda não foi treinado com dados reais de sensores | É necessário validar desempenho com telemetria real |
| A relação entre indicadores ambientais e saúde da colmeia precisa de validação em campo | Exige acompanhamento com especialistas e produtores |
| Os indicadores de florada, biodiversidade e risco ambiental são aproximações iniciais | Devem evoluir com dados reais e validação científica |
| O uso de dados atmosféricos deve ser tratado como camada complementar até validação científica | A interpretação deve ser cautelosa e não conclusiva |

---

## 🧭 Próximos Passos

| Prioridade técnica | Próximo passo |
| :--- | :--- |
| Dados Copernicus | Integrar dados reais do **Copernicus Data Space Ecosystem** |
| Geoprocessamento | Automatizar recortes territoriais em raio de **3 km por colmeia** |
| Índices de vegetação | Calcular **NDVI**, **EVI** e **NDWI** a partir de imagens Sentinel-2 |
| Clima | Incorporar dados climáticos **ERA5-Land** |
| IoT | Integrar leituras reais de sensores IoT |
| Campo | Coletar registros de campo com produtores |
| Validação especialista | Validar rótulos com especialistas em **apicultura**, **meliponicultura** e **sanidade** |
| Modelagem | Re-treinar o modelo com dados reais |
| Produto | Criar um dashboard com mapas, indicadores e alertas |
| Arquitetura | Evoluir o MVP para uma API de classificação em tempo quase real |

---

## 🧪 Possível Evolução Técnica

Uma evolução natural do MVP é separar o sistema em três modelos:

| Modelo | Finalidade |
| :--- | :--- |
| **Classificador de risco da colmeia** | Identificar colmeias em situação normal, atenção ou alerta |
| **Estimador de disponibilidade floral** | Inferir potencial de pasto apícola a partir de vegetação, clima e dados da colmeia |
| **Detector de anomalias ambientais** | Identificar padrões incomuns em regiões monitoradas |

---

## 🌎 Aplicação no Projeto BeeSpace

Este MVP pode ser usado como base para:

| Aplicação | Como contribui para a BeeSpace |
| :--- | :--- |
| Demonstração técnica no hackathon | Mostra a viabilidade do pipeline de dados e IA |
| Validação da arquitetura de dados | Ajuda a testar a integração entre fontes ambientais e sinais da colmeia |
| Apresentação do pipeline Copernicus + colmeia inteligente | Comunica a proposta de valor do projeto |
| Geração de alertas simulados | Demonstra cenários de risco ambiental, produtivo e sanitário |
| Prototipação de dashboard | Apoia visualização de mapas, indicadores e alertas |
| Explicação do papel da inteligência artificial na BeeSpace | Facilita comunicação com banca, parceiros e usuários |

---

## 📌 Aviso Sobre os Dados

> Os dados utilizados neste MVP são **sintéticos** e servem apenas para demonstrar o funcionamento do pipeline.
>
> Eles **não devem ser interpretados como medições reais** de colmeias, vegetação, clima, poluição ou biodiversidade.

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

---

## 👥 Autoria

**Projeto BeeSpace CopernicusLAC Panamá Hackathon 2026**.

MVP de **Machine Learning** para **biovigilância ambiental** com colmeias inteligentes e dados **Copernicus**.
