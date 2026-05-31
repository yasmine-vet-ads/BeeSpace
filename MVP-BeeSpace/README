# BeeSpace ML MVP

<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge&logo=rocket" alt="Status MVP">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Contexto-CopernicusLAC_Hackathon_2026-green?style=for-the-badge&logo=copernicus" alt="Hackathon Context">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License MIT">
</p>

<p align="center">
  <strong>Prova de Conceito de Machine Learning para biovigilância ambiental, sanitária e produtiva com colmeias inteligentes e dados Copernicus.</strong>
</p>

---

## 🎯 Visão Geral

A **BeeSpace** propõe transformar colmeias inteligentes em **biossensores territoriais ativos**. Este repositório contém o MVP (Produto Mínimo Viável) de Machine Learning, desenvolvido como prova de conceito para o **CopernicusLAC Panamá Hackathon 2026**.

Nossa solução conecta dados locais microambientais (sensores IoT, acústica, visão) com dados geoespaciais e climáticos macroambientais do programa **Copernicus**, utilizando inteligência artificial para classificar a saúde da colmeia e o risco do entorno.

> **Tese Central:** Dados Copernicus + Sensores da Colmeia + Inteligência = Alerta Acionável para Biovigilância Ambiental.

## 📌 Tabela de Conteúdos

- [Objetivo do MVP](#-objetivo-do-mvp)
- [Arquitetura de Dados (Prevista)](#-arquitetura-de-dados-prevista)
- [Como o Modelo Funciona](#-como-o-modelo-funciona)
- [Início Rápido](#-início-rápido)
  - [Instalação](#instalação)
  - [Execução](#execução)
- [Limitações e Próximos Passos](#-limitações-e-próximos-passos)
- [Equipe e Contato](#-equipe-e-contato)

---

## 🚀 Objetivo do MVP

O script principal treina e avalia um modelo de classificação que categoriza o estado de cada colmeia inteligente e seu entorno em três níveis de risco:

| Nível | Classe | Significado Biológico/Ambiental |
| :---: | :--- | :--- |
| ✅ | **`normal`** | Colmeia saudável e entorno em condição favorável. |
| ⚠️ | **`atencao`** | Sinais moderados de estresse na colmeia ou risco ambiental/climático detectado. |
| 🚨 | **`alerta`** | Combinação crítica de fatores ambientais adversos e sinais anômalos graves da colmeia. |

---

## 📊 Arquitetura de Dados (Prevista)

*Nota: Este MVP utiliza **dados sintéticos** modelados com base nas estatísticas e distribuições esperadas das fontes reais abaixo.*

### 📡 Macrodados (Programa Copernicus)

<details>
<summary>Clique para expandir as fontes geoespaciais previstas</summary>

| Variável | Fonte Prevista | Interpretação (Vetor de Risco/Saúde) |
| :--- | :--- | :--- |
| **NDVI** | Sentinel-2 / CLMS | Vigor e saúde geral da vegetação circundante. |
| **EVI** | Sentinel-2 | Densidade e atividade vegetal (ajustado para solo). |
| **NDWI** | Sentinel-2 | Conteúdo hídrico (umidade) da vegetação. |
| **temp_media** | C3S / ERA5-Land | Temperatura média histórica/recente da área. |
| **precipitacao_7d** | C3S / ERA5-Land | Chuva acumulada na última semana (impacta forrageamento). |
| **umidade_solo** | C3S / ERA5-Land | Condição hídrica do solo (impacta florada). |
| **poluicao_indice** | Sentinel-5P / CAMS | Indicador de poluentes atmosféricos (potencial estressor). |
| **perc_mata_nativa**| CLMS Land Cover | Proporção de biodiversidade flora nativa no entorno. |
| **perc_agricultura** | CLMS Land Cover | Proporção de monocultura (risco de pesticidas). |

</details>

### 🪵 Microdados (IoT da Colmeia)

<details>
<summary>Clique para expandir as fontes de sensores locais previstas</summary>

| Variável | Fonte Prevista | Interpretação (Sinal Clínico) |
| :--- | :--- | :--- |
| **temp_colmeia** | Sensor Interno DHT | Homeostase térmica do enxame. |
| **umidade_colmeia** | Sensor Interno DHT | Controle hidrométrico interno. |
| **variacao_peso_7d** | Célula de Carga | Indicador de produtividade (estocagem de mel/pólen). |
| **atividade_abelhas**| Visão Computacional| Fluxo de entrada e saída (YOLO na entrada). |
| **anomalia_acustica**| Bioacústica I2S | Assinatura sonora de estresse, ausência de rainha, enxameação. |
| **mortalidade** | Visão/Campo | Registro presencial de mortalidade excessiva. |

</details>

---

## 🧠 Como o Modelo Funciona

O pipeline de Machine Learning é encapsulado no script `beespace_mvp.py`:

```mermaid
graph TD
    A[Geração de Dados Sintéticos] -->|Regras Estatísticas| B(Base Tabular CSV)
    B --> C{Pré-processamento e Divisão Treino/Teste}
    C -->|80% Treino| D[Algoritmo Random Forest]
    C -->|20% Teste| E[Avaliação do Modelo]
    D -->|Treinamento| F(Modelo .pkl Salvo)
    E --> G[Métricas: Precisão, Recall, F1-Score]
    E --> H[Ranking de Importância de Variáveis]
    I[Nova Colmeia Hipotética] --> F
    F -->|Inferência| J(Classificação de Risco: Normal/Atenção/Alerta)
