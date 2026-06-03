<div align="center">

# 🐝 BeeSpace - Módulo Geo-IoT

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/JupyterLab-Copernicus-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-GIS-139C5A?style=for-the-badge&logo=geopandas&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-Interactive%20Maps-77B829?style=for-the-badge)
![IoT](https://img.shields.io/badge/IoT-Smart%20Hives-FFB000?style=for-the-badge)

**Integração espacial de sensores embarcados em colmeias inteligentes para monitoramento ambiental, análise de microclimas e conservação da biodiversidade.**

</div>

---

## 🌍 Visão Geral da Arquitetura

O módulo **Geo-IoT BeeSpace** transforma leituras tabulares de sensores instalados em colmeias em uma camada geoespacial interativa. A proposta é apoiar análises no **JupyterLab do Copernicus**, conectando dados de campo, lógica de alerta ambiental e visualização cartográfica em um único fluxo reprodutível.

> 🛰️ **Objetivo técnico:** representar colmeias como nós IoT georreferenciados, estimar zonas de forrageamento em um raio aproximado de 3 km e destacar automaticamente condições de possível estresse térmico ou hídrico.

### Pipeline do Script

| Etapa | Tecnologia | Resultado |
|---|---|---|
| 1. Simulação dos sensores | `pandas` | DataFrame com variáveis ambientais e produtivas |
| 2. Georreferenciamento | `geopandas` + `shapely` | GeoDataFrame em `EPSG:4326` |
| 3. Visualização webmap | `folium` | Mapa interativo centralizado na Serra Gaúcha |
| 4. Alerta ambiental | Regra lógica Python | Marcadores verdes ou vermelhos conforme risco |

---

## 📊 Dicionário de Dados

| Variável | Tipo | Unidade | Descrição |
|---|---:|---:|---|
| `id_colmeia` | `str` | — | Identificador único da colmeia inteligente na rede BeeSpace. |
| `latitude` | `float` | graus decimais | Coordenada geográfica norte-sul da colmeia em `EPSG:4326`. |
| `longitude` | `float` | graus decimais | Coordenada geográfica leste-oeste da colmeia em `EPSG:4326`. |
| `temp_interna_c` | `float` | °C | Temperatura interna medida pelo sensor embarcado. |
| `umidade_perc` | `float` | % | Umidade relativa registrada no interior ou entorno imediato da colmeia. |
| `peso_kg` | `float` | kg | Peso estimado da colmeia, útil para inferir estoque, atividade e produtividade. |

### 🚨 Regra de Alerta

| Condição | Ícone no mapa | Interpretação |
|---|---|---|
| `temp_interna_c > 35` **ou** `umidade_perc < 40` | 🔴 Vermelho | Possível estresse térmico/hídrico. |
| Demais cenários | 🟢 Verde | Condição ambiental adequada. |

---

## 🧰 Pré-requisitos

Instale as bibliotecas necessárias no ambiente Python do JupyterLab:

```bash
pip install pandas geopandas folium shapely ipython
```

> 💡 Em ambientes Copernicus/JupyterLab, verifique se o kernel selecionado é o mesmo ambiente em que as dependências foram instaladas.

---

## ▶️ Como Usar

1. Abra o diretório do módulo no JupyterLab:

   ```text
   BeeSpace/JupyterLab/Fusão.Macro.Micro/
   ```

2. Execute o script em uma célula do notebook:

   ```python
   %run beespace_geo_iot.py
   ```

3. Interaja com o mapa renderizado:
   - Ative/desative camadas no controle lateral.
   - Clique nos marcadores para visualizar os dados IoT em popup HTML.
   - Observe círculos de aproximadamente **3 km** representando áreas potenciais de forrageamento.

---

## 🗺️ Saídas Esperadas

- **Mapa base interativo** centralizado na média das colmeias simuladas na Serra Gaúcha.
- **Buffers circulares semitransparentes** representando áreas de coleta das abelhas.
- **Marcadores IoT com popup HTML** contendo ID, temperatura, umidade, peso e coordenadas.
- **Alertas visuais automáticos** para apoiar triagem ambiental e decisões de manejo.

---

## 🌱 Aplicação em Conservação

Este módulo oferece uma base para cruzar sinais de colmeias com variáveis ambientais e camadas territoriais, como uso do solo, vegetação, declividade, fragmentos florestais e indicadores climáticos. Com isso, a BeeSpace pode evoluir para uma rede de bioindicadores distribuídos, contribuindo para monitoramento de biodiversidade, agricultura regenerativa e gestão de paisagens produtivas.

---

<div align="center">

**BeeSpace · Colmeias inteligentes como sensores vivos da paisagem** 🐝🌿

</div>
