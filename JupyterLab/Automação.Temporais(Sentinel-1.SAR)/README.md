# 🛰️ BeeSpace - Radar Automático (Sentinel-1)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![STAC API](https://img.shields.io/badge/STAC-API-2C7A7B?style=for-the-badge)
![Sentinel-1 SAR](https://img.shields.io/badge/Sentinel--1-SAR-0B3D91?style=for-the-badge)
![JupyterLab](https://img.shields.io/badge/JupyterLab-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Geospatial-139C5A?style=for-the-badge)

> **Objetivo:** automatizar a descoberta de cenas Sentinel-1 GRD para alertas precoces de desmatamento no raio de forrageamento das colmeias inteligentes BeeSpace, priorizando monitoramento contínuo mesmo em regiões úmidas, montanhosas e com alta nebulosidade.

---

## Por que Radar SAR é essencial para a BeeSpace?

Sensores ópticos, como Sentinel-2, dependem de iluminação solar e são fortemente afetados por nuvens, fumaça e sombras topográficas. Em paisagens da **Serra Gaúcha**, onde a umidade e a orografia favorecem cobertura persistente de nuvens, isso pode criar lacunas críticas justamente durante eventos de supressão vegetal.

O **Radar de Abertura Sintética (SAR)** do Sentinel-1 opera em micro-ondas e emite sua própria energia, permitindo observações:

| Capacidade SAR | Impacto no monitoramento ecológico |
|---|---|
| Atravessa nuvens e fumaça | Mantém a vigilância mesmo em períodos chuvosos ou com queimadas próximas. |
| Opera de dia e de noite | Reduz dependência de horário e iluminação solar. |
| Sensível à estrutura do dossel | Ajuda a detectar alterações em rugosidade, biomassa e umidade da vegetação. |
| Revisita orbital frequente | Favorece séries temporais para alertas de mudança no entorno das colmeias. |

> Para uma rede de colmeias inteligentes, a continuidade temporal é tão importante quanto a resolução espacial: perdas repentinas de vegetação podem afetar disponibilidade floral, microclima, abrigo e conectividade de habitat.

---

## Pré-requisitos

Instale os pacotes em um ambiente Python usado pelo JupyterLab:

```bash
python -m pip install pystac-client pandas geopandas shapely requests
```

Recomendação para ambientes isolados:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pystac-client pandas geopandas shapely requests jupyterlab
```

### Bibliotecas usadas

| Biblioteca | Função no pipeline |
|---|---|
| `pystac_client` | Conexão com o catálogo STAC público e busca de itens Sentinel-1. |
| `pandas` | Organização tabular dos metadados retornados. |
| `geopandas` | Representação geoespacial da área de interesse. |
| `datetime` | Cálculo dinâmico da janela dos últimos 30 dias. |
| `shapely` | Construção da geometria da bounding box. |

---

## Como executar

1. Abra o JupyterLab na raiz do projeto BeeSpace:

   ```bash
   jupyter lab
   ```

2. Navegue até:

   ```text
   JupyterLab/Automação.Temporais(Sentinel-1.SAR)/
   ```

3. Abra ou importe o script `sentinel1_stac_metadata.py`.

4. Execute a consulta em uma célula:

   ```python
   %run sentinel1_stac_metadata.py
   ```

5. Alternativamente, importe as funções em um notebook:

   ```python
   from sentinel1_stac_metadata import (
       BBOX_SERRA_GAUCHA,
       build_datetime_interval,
       search_sentinel1_metadata,
   )

   df = search_sentinel1_metadata(
       bbox=BBOX_SERRA_GAUCHA,
       datetime_interval=build_datetime_interval(),
   )
   df
   ```

O script consulta o catálogo **Earth Search STAC** da AWS/Element 84, filtra a coleção `sentinel-1-grd` pelo modo `IW` e retorna apenas metadados, sem baixar imagens SAR pesadas.

---

## Estrutura do retorno

O DataFrame final contém os campos operacionais necessários para triagem inicial de cenas:

| Campo | Tipo esperado | Significado técnico | Uso na BeeSpace |
|---|---:|---|---|
| `Data_Aquisicao` | `str/datetime` | Data e hora UTC da aquisição Sentinel-1. | Ordenar cenas recentes e compor séries temporais. |
| `ID_Cena` | `str` | Identificador único da cena no catálogo STAC. | Rastreabilidade, auditoria e posterior download seletivo. |
| `Orbita` | `str` | Estado orbital: `Ascending` ou `Descending`. | Comparar geometrias de visada e reduzir falsos positivos topográficos. |
| `Polarizacoes_Disponiveis` | `str` | Polarizações SAR disponíveis, como `VV` e `VH`. | Avaliar mudanças estruturais e de biomassa no dossel. |

### Interpretação das polarizações VV/VH

| Polarização | Leitura física simplificada | Aplicação em vegetação |
|---|---|---|
| `VV` | Transmissão vertical e recepção vertical. | Sensível a rugosidade superficial, umidade e componentes verticais do alvo. |
| `VH` | Transmissão vertical e recepção horizontal. | Frequentemente útil para vegetação por capturar espalhamento volumétrico do dossel. |
| `VV + VH` | Combinação multicanal. | Melhora a separação entre floresta preservada, áreas abertas e mudanças abruptas de cobertura. |

> Em alertas de desmatamento, quedas ou mudanças anômalas na resposta `VH`, combinadas com alterações em `VV`, podem indicar remoção de biomassa, abertura de clareiras ou degradação estrutural. A etapa deste script é apenas a **descoberta de metadados**; análises radiométricas devem ser feitas posteriormente com dados calibrados e corrigidos por terreno.

---

## Resiliência operacional

O script inclui blocos `try/except` para capturar falhas comuns em ambientes de campo e notebooks corporativos:

- indisponibilidade temporária da API STAC;
- timeouts de rede;
- erros HTTP;
- falhas inesperadas durante a leitura dos itens.

Em caso de falha, a rotina retorna um DataFrame vazio com o schema esperado, preservando a estabilidade de pipelines posteriores.

---

## Próximos passos recomendados

1. Adicionar filtros por órbita relativa para comparar sempre geometrias semelhantes.
2. Baixar apenas assets selecionados após triagem por metadados.
3. Aplicar calibração radiométrica, speckle filtering e correção de terreno.
4. Construir índices temporais baseados em `VV`, `VH` e razão `VH/VV`.
5. Integrar alertas ao backend BeeSpace para notificar risco ecológico no entorno das colmeias.
