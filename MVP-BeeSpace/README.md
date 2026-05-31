# BeeSpace ML MVP

<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge" alt="Status MVP">
  <img src="https://img.shields.io/badge/Contexto-CopernicusLAC_Hackathon_2026-green?style=for-the-badge&logo=copernicus" alt="Hackathon Context">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License MIT">
</p>

## 📄 Sobre o Projeto

A **BeeSpace** propõe uma solução inovadora de **biovigilância territorial**. Nossa missão é transformar colmeias inteligentes em biossensores territoriais ativos, conectando dados locais das colmeias com dados geoespaciais e climáticos do programa **Copernicus**.

Esta solução busca apoiar produtores, pesquisadores, empresas parceiras e iniciativas de proteção da biodiversidade. Utilizamos indicadores baseados em uma abordagem multidisciplinar que une:
* Dados de campo e sensores IoT;
* Visão computacional e bioacústica;
* Observação da Terra (Satélites).

---

## 🎯 Objetivo do MVP (Prova de Conceito)

Este repositório contém o **MVP de Machine Learning** desenvolvido como prova de conceito para o projeto BeeSpace no contexto do **CopernicusLAC Panamá Hackathon 2026**.

O objetivo principal é demonstrar como dados macroambientais (satélite) e microambientais (sensores locais) podem ser integrados em um *pipeline* de Machine Learning para classificar o estado de saúde e segurança de uma colmeia monitorada.

A tese central demonstrada é:
> **Dados Copernicus + Sensores da Colmeia + Inteligência de Dados = Alerta Acionável para Biovigilância Ambiental.**

---

## 🧠 Como o Modelo Funciona

O script `beespace_mvp.py` encapsula todo o pipeline de ML em um algoritmo de **Classificação**, categorizando cada colmeia em uma das seguintes classes:

| Classe | Significado |
| :--- | :--- |
| 🟢 **`normal`** | Colmeia e entorno em condição favorável. |
| 🟡 **`atencao`** | Sinais moderados de risco ambiental, climático, produtivo ou sanitário. |
| 🔴 **`alerta`** | Combinação crítica de fatores ambientais adversos e sinais anômalos graves na colmeia. |

### Modelo Utilizado
O MVP utiliza o algoritmo **RandomForestClassifier** (da biblioteca *scikit-learn*). A escolha justifica-se pois o Random Forest:
1.  Funciona bem com dados tabulares e heterogêneos;
2.  Combina eficientemente variáveis ambientais (contínuas) e de sensores;
3.  Permite capturar relações não-lineares;
4.  Oferece explicabilidade através da análise de importância das variáveis (*feature importance*);
5.  É robusto e adequado para uma demonstração técnica em contexto de *hackathon*.

---

## 📊 Arquitetura de Dados (Prevista vs. Sintética)

⚠️ **AVISO IMPORTANTE:** Este MVP utiliza **dados sintéticos** gerados programaticamente. Eles não representam medições reais, servindo apenas para demonstrar o funcionamento do pipeline e da lógica do modelo.

A arquitetura foi modelada considerando as seguintes fontes reais previstas:

### 📡 Macrodados (Copernicus & Ambiental)

| Variável | Fonte Prevista | Interpretação |
| :--- | :--- | :--- |
| `ndvi` | Sentinel-2 / CLMS | Vigor da vegetação |
| `evi` | Sentinel-2 | Densidade e atividade vegetal |
| `ndwi` | Sentinel-2 | Umidade da vegetação |
| `temp_media` | C3S / ERA5-Land | Temperatura média da área |
| `precipitacao_7d` | C3S / ERA5-Land | Chuva acumulada nos últimos 7 dias |
| `umidade_solo` | C3S / ERA5-Land | Condição hídrica do solo |
| `poluicao_indice` | Sentinel-5P / CAMS | Indicador de poluição atmosférica |
| `perc_mata_nativa`| CLMS Land Cover | Proporção de vegetação nativa no entorno |
| `perc_agricultura` | CLMS Land Cover | Proporção de agricultura ou monocultura |
| `perc_solo_exposto`| CLMS Land Cover | Proporção de solo exposto |

### 🪵 Microdados (Colmeia Inteligente)

| Variável | Fonte Prevista | Interpretação |
| :--- | :--- | :--- |
| `temp_colmeia` | Sensor interno | Temperatura interna da colmeia |
| `umidade_colmeia` | Sensor interno | Umidade interna da colmeia |
| `variacao_peso_7d`| Célula de carga | Ganho ou perda de peso acumulado em 7 dias |
| `atividade_abelhas`| Visão computacional | Fluxo de entrada e saída de abelhas |
| `anomalia_acustica`| Bioacústica | Presença de sinais sonoros anômalos |
| `mortalidade_observada`| Visão/Campo | Registro presencial de mortalidade excessiva |

---

## 📂 Estrutura do Repositório

```text
beespace-ml-mvp/
├── README.md                       # Este arquivo
├── beespace_mvp.py                 # Script Python principal (MVP)
├── requirements.txt                # Dependências do projeto
├── dados_sinteticos_beespace.csv   # Base de dados gerada (após execução)
└── modelo_beespace_mvp.pkl         # Modelo treinado salvo (após execução)
