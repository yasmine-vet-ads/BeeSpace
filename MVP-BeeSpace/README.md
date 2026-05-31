# 🐝 BeeSpace ML MVP

![Status](https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge)
![Hackathon](https://img.shields.io/badge/Contexto-CopernicusLAC_Panam%C3%A1_2026-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**MVP de Machine Learning para classificação de risco ambiental, produtivo e sanitário em colmeias inteligentes**, desenvolvido como prova de conceito para o projeto BeeSpace no contexto do CopernicusLAC Panamá Hackathon 2026.

---

## 🌍 Sobre o projeto

A **BeeSpace** propõe transformar colmeias inteligentes em biossensores territoriais, conectando dados locais das colmeias com dados geoespaciais e climáticos do programa Copernicus.

A solução busca apoiar produtores, pesquisadores, empresas parceiras e iniciativas de proteção da biodiversidade por meio de indicadores baseados em dados de campo, sensores IoT, visão computacional, bioacústica e observação da Terra.

Neste MVP, o objetivo é demonstrar como dados macroambientais e microambientais podem ser integrados em um pipeline de Machine Learning para classificar o estado de uma colmeia monitorada.

---

## 🎯 Objetivo do MVP

O script classifica cada colmeia inteligente em uma das seguintes classes:

| Classe | Significado |
| :--- | :--- |
| 🟢 **normal** | Colmeia e entorno em condição favorável |
| 🟡 **atencao** | Sinais moderados de risco ambiental, climático, produtivo ou sanitário |
| 🔴 **alerta** | Combinação crítica de fatores ambientais e sinais anômalos da colmeia |

A prova de conceito demonstra a lógica central da BeeSpace:
> **Dados Copernicus + sensores da colmeia + inteligência de dados = alerta acionável para biovigilância ambiental.**

---

## 📊 Fontes de dados previstas

Este MVP utiliza dados sintéticos, mas foi modelado considerando as fontes reais previstas na arquitetura da BeeSpace.

### 🛰️ Dados Copernicus e ambientais

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

## ⚙️ Como o modelo funciona

O script executa as seguintes etapas:
1. Gera uma base sintética com variáveis ambientais, territoriais e da colmeia.
2. Cria uma regra inicial de rotulagem para simular as classes `normal`, `atencao` e `alerta`.
3. Treina um modelo de classificação usando Random Forest.
4. Avalia o desempenho com matriz de confusão e relatório de classificação.
5. Calcula a importância das variáveis para apoiar a explicabilidade.
6. Simula a previsão de risco para uma nova colmeia.
7. Salva o modelo treinado e a base sintética em arquivos locais.

### Modelo utilizado
O MVP utiliza o algoritmo `RandomForestClassifier`, da biblioteca `scikit-learn`. A escolha do Random Forest se justifica porque ele:
* Funciona bem com dados tabulares;
* Combina variáveis ambientais, climáticas e de sensores;
* Permite capturar relações não lineares;
* É robusto para uma prova de conceito;
* Permite analisar a importância das variáveis;
* É mais fácil de explicar em um contexto de hackathon.

---

## 📂 Estrutura sugerida do repositório

```text
beespace-ml-mvp/
├── README.md
├── beespace_mvp.py
├── requirements.txt
├── dados_sinteticos_beespace.csv
└── modelo_beespace_mvp.pkl
