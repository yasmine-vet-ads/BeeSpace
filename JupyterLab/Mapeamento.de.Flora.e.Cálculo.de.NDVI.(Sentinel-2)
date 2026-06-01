"""
BeeSpace | NDVI com Sentinel-2 L2A no JupyterLab do Copernicus
================================================================

Objetivo
--------
Processar duas bandas raster locais do Sentinel-2 L2A em formato GeoTIFF
(.tif) e calcular o NDVI de uma área de forrageamento monitorada pela BeeSpace.

Bandas usadas
-------------
- B04 / Vermelho: reflectância no vermelho, sensível à absorção pela clorofila.
- B08 / NIR: reflectância no infravermelho próximo, alta em vegetação saudável.

Fórmula
-------
NDVI = (NIR - Vermelho) / (NIR + Vermelho)

Interpretação rápida
--------------------
- NDVI alto, próximo de 1: vegetação mais vigorosa.
- NDVI intermediário, próximo de 0: solo exposto, áreas urbanas ou vegetação rala.
- NDVI negativo: água, sombra, nuvens ou superfícies sem vegetação fotossintética.

Como usar no notebook
---------------------
1. Ajuste as variáveis `CAMINHO_BANDA_4_VERMELHO` e `CAMINHO_BANDA_8_NIR`.
2. Execute a célula para carregar as funções.
3. Remova o comentário das duas últimas linhas da seção "Exemplo de execução".
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio


# -----------------------------------------------------------------------------
# 1) Caminhos dos arquivos locais
# -----------------------------------------------------------------------------
# Substitua estes caminhos pelos arquivos .tif da sua cena Sentinel-2 L2A.
# Em produtos Sentinel-2, os nomes dos arquivos normalmente contêm "B04" para
# a banda vermelha e "B08" para a banda do infravermelho próximo.
CAMINHO_BANDA_4_VERMELHO = Path("./dados/Sentinel2_L2A_B04.tif")
CAMINHO_BANDA_8_NIR = Path("./dados/Sentinel2_L2A_B08.tif")


# -----------------------------------------------------------------------------
# 2) Função principal: leitura das bandas e cálculo do NDVI
# -----------------------------------------------------------------------------
def calcular_ndvi(caminho_vermelho, caminho_nir):
    """
    Lê a Banda 4 (Vermelho) e a Banda 8 (NIR) e calcula o NDVI.

    Parâmetros
    ----------
    caminho_vermelho : str ou pathlib.Path
        Caminho local para o arquivo GeoTIFF da Banda 4 (B04 - Vermelho).
    caminho_nir : str ou pathlib.Path
        Caminho local para o arquivo GeoTIFF da Banda 8 (B08 - NIR).

    Retorna
    -------
    ndvi : numpy.ndarray
        Matriz 2D com valores de NDVI em float32. Pixels sem dados, inválidos
        ou com denominador zero são preenchidos com np.nan.
    perfil_saida : dict
        Perfil rasterio baseado na banda vermelha, já ajustado para uma possível
        exportação futura do NDVI em GeoTIFF com uma banda float32 e NoData NaN.
    extensao_plot : tuple
        Extensão espacial no formato (xmin, xmax, ymin, ymax), útil para plotar
        o raster com coordenadas reais quando a transformação espacial permitir.
    """

    caminho_vermelho = Path(caminho_vermelho)
    caminho_nir = Path(caminho_nir)

    # Abrimos os dois rasters ao mesmo tempo. Cada arquivo raster é uma matriz
    # georreferenciada: linhas e colunas representam pixels, enquanto o valor de
    # cada pixel representa a reflectância daquela banda espectral.
    with (
        rasterio.open(caminho_vermelho) as raster_vermelho,
        rasterio.open(caminho_nir) as raster_nir,
    ):
        # O NDVI é uma operação pixel a pixel. Por isso, as duas bandas precisam
        # ter a mesma quantidade de linhas e colunas. Se não tiverem, é sinal de
        # que é necessário reprojetar, recortar ou reamostrar uma das bandas.
        if raster_vermelho.shape != raster_nir.shape:
            raise ValueError(
                "As bandas B04 e B08 possuem dimensões diferentes. "
                "Use rasters já alinhados antes de calcular o NDVI."
            )

        # Além das dimensões, é importante confirmar se a grade espacial é a
        # mesma. Dois rasters podem ter o mesmo tamanho, mas representar áreas ou
        # resoluções diferentes. O transform descreve origem, pixel size e rotação;
        # o CRS descreve o sistema de coordenadas.
        if raster_vermelho.transform != raster_nir.transform:
            raise ValueError(
                "As bandas B04 e B08 têm transformações espaciais diferentes. "
                "Alinhe as grades antes de executar o cálculo."
            )

        if raster_vermelho.crs != raster_nir.crs:
            raise ValueError(
                "As bandas B04 e B08 estão em sistemas de coordenadas diferentes. "
                "Reprojete uma delas para o mesmo CRS antes de calcular o NDVI."
            )

        # read(1, masked=True) lê a primeira banda do GeoTIFF como um
        # numpy.ma.MaskedArray. Isso preserva uma máscara para pixels NoData,
        # permitindo que áreas sem informação sejam ignoradas no cálculo.
        banda_vermelha = raster_vermelho.read(1, masked=True).astype("float32")
        banda_nir = raster_nir.read(1, masked=True).astype("float32")

        # Copiamos os metadados da banda vermelha. O NDVI terá a mesma grade,
        # transformada espacial e CRS da imagem original, mas com uma única banda
        # float32 e valores ausentes representados por NaN.
        perfil_saida = raster_vermelho.profile.copy()
        perfil_saida.update(count=1, dtype="float32", nodata=np.nan)

        # bounds contém a caixa espacial do raster. Essa extensão será usada no
        # gráfico para que os eixos representem coordenadas do raster, e não
        # apenas índices de linha e coluna.
        bounds = raster_vermelho.bounds
        extensao_plot = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    # -------------------------------------------------------------------------
    # Manipulação matricial com NumPy
    # -------------------------------------------------------------------------
    # A fórmula do NDVI é aplicada sobre matrizes completas, não pixel a pixel em
    # loops Python. Isso é chamado de vetorização e é muito mais eficiente para
    # imagens de satélite, que podem ter milhões de pixels.
    numerador = banda_nir - banda_vermelha
    denominador = banda_nir + banda_vermelha

    # Montamos uma máscara booleana para identificar tudo que deve ser ignorado:
    # - pixels NoData da banda vermelha;
    # - pixels NoData da banda NIR;
    # - pixels cujo denominador é zero, pois NDVI dividiria por zero;
    # - pixels cujo denominador já seja inválido por qualquer outro motivo.
    mascara_invalida = (
        np.ma.getmaskarray(banda_vermelha)
        | np.ma.getmaskarray(banda_nir)
        | np.ma.getmaskarray(denominador)
        | (np.ma.filled(denominador, 0) == 0)
    )

    # Criamos uma matriz comum, preenchida com NaN. Em seguida, calculamos o NDVI
    # apenas nos pixels válidos. Assim, evitamos divisão por zero e impedimos que
    # valores NoData entrem na estatística ou no mapa final.
    ndvi = np.full(banda_vermelha.shape, np.nan, dtype="float32")

    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi[~mascara_invalida] = (
            numerador[~mascara_invalida] / denominador[~mascara_invalida]
        )

    # Qualquer valor residual infinito ou não numérico é substituído por NaN. O
    # Matplotlib ignora NaN no desenho do mapa, deixando esses pixels sem cor.
    ndvi[~np.isfinite(ndvi)] = np.nan

    # Por segurança, limitamos o resultado ao intervalo físico esperado do NDVI.
    # Pequenos desvios podem ocorrer por ruído, escala inadequada ou pixels
    # problemáticos; o clipping evita que eles distorçam a escala de cores.
    ndvi = np.clip(ndvi, -1, 1).astype("float32")

    return ndvi, perfil_saida, extensao_plot


# -----------------------------------------------------------------------------
# 3) Função de visualização: mapa NDVI com RdYlGn e colorbar
# -----------------------------------------------------------------------------
def plotar_ndvi(
    ndvi,
    extensao=None,
    titulo="NDVI - Área de Forrageamento BeeSpace",
):
    """
    Plota o NDVI com o mapa de cores RdYlGn e uma barra de cores.

    Parâmetros
    ----------
    ndvi : numpy.ndarray
        Matriz 2D de NDVI retornada por `calcular_ndvi`.
    extensao : tuple ou None
        Extensão espacial no formato (xmin, xmax, ymin, ymax). Se for None, os
        eixos mostram índices de pixel.
    titulo : str
        Título do mapa.
    """

    # Criamos uma figura em tamanho confortável para uso em notebook.
    fig, ax = plt.subplots(figsize=(10, 8))

    # O cmap RdYlGn segue a lógica vermelho -> amarelo -> verde:
    # - vermelho: NDVI baixo;
    # - amarelo: NDVI intermediário;
    # - verde: NDVI alto.
    imagem = ax.imshow(
        ndvi,
        cmap="RdYlGn",
        vmin=-1,
        vmax=1,
        extent=extensao,
    )

    ax.set_title(titulo)

    if extensao is None:
        ax.set_xlabel("Coluna do raster")
        ax.set_ylabel("Linha do raster")
    else:
        ax.set_xlabel("Coordenada X")
        ax.set_ylabel("Coordenada Y")

    # A colorbar transforma o mapa em um produto interpretável, pois permite
    # relacionar cada cor ao valor numérico de NDVI.
    colorbar = fig.colorbar(imagem, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("NDVI")

    plt.tight_layout()
    plt.show()

    return fig, ax


# -----------------------------------------------------------------------------
# 4) Função opcional: exportar o NDVI como GeoTIFF
# -----------------------------------------------------------------------------
def salvar_ndvi_geotiff(ndvi, perfil_saida, caminho_saida):
    """
    Salva a matriz NDVI em um GeoTIFF georreferenciado.

    Esta etapa é opcional, mas útil se você quiser abrir o resultado em um SIG
    como QGIS, ArcGIS ou outro notebook de análise espacial.
    """

    caminho_saida = Path(caminho_saida)

    with rasterio.open(caminho_saida, "w", **perfil_saida) as destino:
        destino.write(ndvi.astype("float32"), 1)

    print(f"NDVI salvo em: {caminho_saida}")


# -----------------------------------------------------------------------------
# 5) Exemplo de execução no JupyterLab
# -----------------------------------------------------------------------------
# Depois de ajustar os caminhos no início do script, descomente as linhas abaixo:
#
# ndvi_forrageamento, perfil_ndvi, extensao_ndvi = calcular_ndvi(
#     CAMINHO_BANDA_4_VERMELHO,
#     CAMINHO_BANDA_8_NIR,
# )
#
# plotar_ndvi(ndvi_forrageamento, extensao=extensao_ndvi)
#
# Opcional: exportar o resultado para GeoTIFF.
# salvar_ndvi_geotiff(
#     ndvi_forrageamento,
#     perfil_ndvi,
#     "./resultados/ndvi_area_forrageamento_beespace.tif",
# )
