"""
BeeSpace | Análise Topográfica para Microclimas com DEM Copernicus
===================================================================

Código pronto para executar em UMA ÚNICA CÉLULA do JupyterLab.

Objetivo:
- Ler um Modelo Digital de Elevação (DEM) em GeoTIFF.
- Imprimir o CRS para conferir a referência espacial.
- Calcular Declividade (Slope) para apoiar análise de corredores de vento.
- Calcular Orientação da Encosta (Aspect) para apoiar análise de incidência solar.
- Plotar DEM, Declividade e Aspect em três subplots lado a lado.

Bibliotecas principais:
- rasterio: leitura geoespacial do GeoTIFF e metadados, como CRS e transform.
- richdem: cálculo dos atributos topográficos slope e aspect.
- matplotlib: visualização dos mapas em uma única figura.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
import richdem as rd


# -----------------------------------------------------------------------------
# 1) Configure aqui o caminho local do DEM Copernicus em GeoTIFF
# -----------------------------------------------------------------------------
# Substitua pelo arquivo real do seu ambiente JupyterLab/Copernicus.
# Exemplo: Path("./dados/Copernicus_DEM_area_colmeias.tif")
CAMINHO_DEM = Path("./dados/Copernicus_DEM_area_colmeias.tif")


# -----------------------------------------------------------------------------
# 2) Leitura do DEM com rasterio e inspeção espacial
# -----------------------------------------------------------------------------
# O raster DEM é uma matriz 2D: cada célula/pixel guarda a altitude do terreno.
# Além dos valores de altitude, o arquivo GeoTIFF contém metadados espaciais
# essenciais para geoprocessamento: CRS, transformada affine, resolução e bounds.
with rasterio.open(CAMINHO_DEM) as src:
    # read(1, masked=True) lê a primeira banda como uma matriz mascarada.
    # Pixels NoData são marcados na máscara e não entram corretamente nos cálculos.
    dem_mascarado = src.read(1, masked=True).astype("float32")

    # Metadados espaciais do raster.
    crs = src.crs
    transform = src.transform
    bounds = src.bounds
    resolucao_x, resolucao_y = src.res
    nodata_original = src.nodata

    # Extensão usada no imshow para desenhar o raster em coordenadas reais.
    extensao = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    print("===== Informações espaciais do DEM =====")
    print(f"Arquivo: {CAMINHO_DEM}")
    print(f"CRS: {crs}")
    print(f"Resolução espacial: {resolucao_x} x {resolucao_y}")
    print(f"Dimensões da matriz: {src.width} colunas x {src.height} linhas")
    print(f"Valor NoData original: {nodata_original}")

    if crs is None:
        print(
            "ATENÇÃO: o DEM não possui CRS definido. "
            "Defina/reprojete o raster antes de usar os resultados em decisão espacial."
        )
    elif crs.is_geographic:
        print(
            "ATENÇÃO: o CRS é geográfico, ou seja, as unidades horizontais estão "
            "em graus. Para declividade mais precisa, reprojete o DEM para um CRS "
            "projetado em metros, como UTM da área de estudo."
        )
    else:
        print(
            "CRS projetado detectado. As unidades horizontais provavelmente estão "
            "em metros, o que é mais adequado para cálculo de declividade."
        )


# -----------------------------------------------------------------------------
# 3) Preparação da matriz para o richdem
# -----------------------------------------------------------------------------
# O richdem trabalha muito bem com arrays NumPy/richdem. Para isso, convertemos
# a matriz mascarada do rasterio para uma matriz comum, preenchendo NoData com um
# valor sentinela. Esse valor será informado ao richdem para ser ignorado.
valor_nodata = nodata_original if nodata_original is not None else -9999.0
mascara_nodata = np.ma.getmaskarray(dem_mascarado)
dem_array = dem_mascarado.filled(valor_nodata).astype("float32")

# Criamos um rdarray, que é o formato usado pelo richdem para calcular atributos
# de terreno. Também transferimos a transformada espacial e o CRS para preservar
# a relação entre pixels e coordenadas.
dem_richdem = rd.rdarray(dem_array, no_data=valor_nodata)
dem_richdem.geotransform = transform.to_gdal()
if crs is not None:
    dem_richdem.projection = crs.to_wkt()


# -----------------------------------------------------------------------------
# 4) Cálculo dos atributos topográficos
# -----------------------------------------------------------------------------
# Declividade (slope_degrees): ângulo de inclinação do terreno em graus.
# - Valores baixos indicam áreas planas.
# - Valores altos indicam encostas mais íngremes, relevantes para vento,
#   drenagem, acesso e estabilidade de instalação das colmeias.
declividade = rd.TerrainAttribute(dem_richdem, attrib="slope_degrees")

# Orientação da Encosta (aspect): direção para onde a encosta está voltada,
# em graus azimutais.
# - 0/360°: Norte
# - 90°: Leste
# - 180°: Sul
# - 270°: Oeste
# Esse atributo ajuda a inferir incidência solar, aquecimento do terreno e
# possíveis variações microclimáticas ao redor das colmeias.
orientacao = rd.TerrainAttribute(dem_richdem, attrib="aspect")

# Convertendo os resultados para arrays NumPy comuns para facilitar plotagem.
dem_plot = dem_mascarado.filled(np.nan).astype("float32")
declividade_plot = np.asarray(declividade, dtype="float32")
orientacao_plot = np.asarray(orientacao, dtype="float32")

# Mantemos os pixels NoData como NaN em todos os mapas. O matplotlib não colore
# NaN, evitando que áreas sem dados sejam interpretadas como terreno válido.
declividade_plot[mascara_nodata] = np.nan
orientacao_plot[mascara_nodata] = np.nan

# Em muitos algoritmos, áreas perfeitamente planas podem receber aspect negativo
# ou indefinido. Essas células não têm orientação de encosta, então usamos NaN.
orientacao_plot[orientacao_plot < 0] = np.nan


# -----------------------------------------------------------------------------
# 5) Plotagem: DEM, Declividade e Orientação lado a lado
# -----------------------------------------------------------------------------
fig, eixos = plt.subplots(1, 3, figsize=(21, 6), constrained_layout=True)

# Mapa 1: DEM original.
im_dem = eixos[0].imshow(dem_plot, cmap="terrain", extent=extensao)
eixos[0].set_title("DEM Copernicus\nElevação do terreno")
eixos[0].set_xlabel("Coordenada X")
eixos[0].set_ylabel("Coordenada Y")
cb_dem = fig.colorbar(im_dem, ax=eixos[0], fraction=0.046, pad=0.04)
cb_dem.set_label("Elevação (m)")

# Mapa 2: Declividade.
im_slope = eixos[1].imshow(declividade_plot, cmap="magma", extent=extensao)
eixos[1].set_title("Declividade (Slope)\nCorredores de vento e estabilidade")
eixos[1].set_xlabel("Coordenada X")
eixos[1].set_ylabel("Coordenada Y")
cb_slope = fig.colorbar(im_slope, ax=eixos[1], fraction=0.046, pad=0.04)
cb_slope.set_label("Graus")

# Mapa 3: Orientação da Encosta.
# O colormap twilight_shifted é circular, apropriado para variáveis direcionais
# em graus, pois 0° e 360° representam a mesma direção.
im_aspect = eixos[2].imshow(
    orientacao_plot,
    cmap="twilight_shifted",
    vmin=0,
    vmax=360,
    extent=extensao,
)
eixos[2].set_title("Orientação da Encosta (Aspect)\nIncidência solar")
eixos[2].set_xlabel("Coordenada X")
eixos[2].set_ylabel("Coordenada Y")
cb_aspect = fig.colorbar(im_aspect, ax=eixos[2], fraction=0.046, pad=0.04)
cb_aspect.set_label("Azimute (graus)")

# Título geral da figura para contextualizar a decisão BeeSpace.
fig.suptitle(
    "BeeSpace | Análise Topográfica para Microclimas e Instalação de Colmeias",
    fontsize=16,
    fontweight="bold",
)

plt.show()
