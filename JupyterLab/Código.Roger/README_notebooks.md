# Notebooks BeeSpace para JupyterLab

Este pacote contém notebooks de prova de conceito para reforçar o uso de dados Copernicus, sensores de colmeias e Machine Learning no projeto BeeSpace.

## Notebooks incluídos

1. `00_beespace_pipeline_integrado.ipynb`
   - Pipeline completo com colmeia georreferenciada, área de 3 km, dados Copernicus simulados, sensores, classificação e alerta.

2. `01_ndvi_sentinel2_beespace.ipynb`
   - Cálculo e interpretação de NDVI a partir de bandas Sentinel-2 simuladas.

3. `02_geo_iot_colmeias.ipynb`
   - Colmeias georreferenciadas com área potencial de biovigilância e mapa opcional com Folium.

4. `03_clms_landcover_beespace.ipynb`
   - Simulação de uso e cobertura do solo para estimar qualidade do entorno apícola.

5. `04_era5_climate_beespace.ipynb`
   - Simulação de variáveis climáticas inspiradas em ERA5-Land/C3S.

6. `05_ml_risco_colmeia_beespace.ipynb`
   - MVP de Machine Learning para classificar colmeias em normal, atencao ou alerta.

## Observação

Os notebooks usam dados sintéticos para demonstrar a arquitetura do projeto. Em versão operacional, os dados simulados devem ser substituídos por dados Copernicus, sensores IoT, visão computacional, bioacústica e registros de campo.
