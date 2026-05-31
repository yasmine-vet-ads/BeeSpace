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
| :---: | :--- |
| 🟢 **normal** | Colmeia e entorno em condição favorável. |
| 🟡 **atencao** | Sinais moderados de risco ambiental, climático, produtivo ou sanitário. |
| 🔴 **alerta** | Combinação crítica de fatores ambientais e sinais anômalos da colmeia. |

A prova de conceito demonstra a lógica central da BeeSpace:
> **Dados Copernicus + Sensores da colmeia + Inteligência de dados = Alerta acionável para biovigilância ambiental.**

---

## ⚙️ Arquitetura e Fluxo de Dados

O diagrama abaixo ilustra como as fontes de dados convergem no nosso modelo (suportado nativamente pelo GitHub via Mermaid):

```mermaid
graph TD
    A[Satélites Copernicus] -->|NDVI, Clima, Poluição| C(Motor de IA BeeSpace - Random Forest)
    B[Sensores IoT da Colmeia] -->|Peso, Áudio, Clima Interno| C
    C --> D{Classificação de Risco}
    D -->|🟢 Normal| E[Dashboard do Produtor]
    D -->|🟡 Atenção| E
    D -->|🔴 Alerta| F[Notificação ESG / Defesa Sanitária]
