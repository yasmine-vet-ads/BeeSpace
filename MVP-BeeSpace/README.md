# 🐝 BeeSpace ML MVP

<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge" alt="Status MVP">
  <img src="https://img.shields.io/badge/Contexto-CopernicusLAC_Panam%C3%A1_2026-blue?style=for-the-badge" alt="Hackathon Context">
  <img src="https://img.shields.io/badge/Python-3.10%2B-green?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License MIT">
</p>

> **MVP de Machine Learning para classificação de risco ambiental, produtivo e sanitário em colmeias inteligentes**, desenvolvido como prova de conceito para o projeto BeeSpace no contexto do CopernicusLAC Panamá Hackathon 2026.

---

## 🌍 Sobre o projeto

A BeeSpace propõe transformar colmeias inteligentes em biossensores territoriais, conectando dados locais das colmeias com dados geoespaciais e climáticos do programa Copernicus.

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

### 🧠 Modelo utilizado
O MVP utiliza o algoritmo `RandomForestClassifier`, da biblioteca scikit-learn.

A escolha do Random Forest se justifica porque ele:
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

🚀 Instalação e Execução📋 RequisitosPython 3.10 ou superiorNumPyPandasScikit-learnJoblib🛠️ InstalaçãoClone o repositório:Bashgit clone [https://github.com/seu-usuario/beespace-ml-mvp.git](https://github.com/seu-usuario/beespace-ml-mvp.git)
cd beespace-ml-mvp
Crie um ambiente virtual:Bashpython -m venv venv
Ative o ambiente virtual:No Windows:DOSvenv\Scripts\activate
No Linux ou macOS:Bashsource venv/bin/activate
Instale as dependências:Bashpip install -r requirements.txt
Nota: Caso ainda não exista, crie um arquivo requirements.txt com o seguinte conteúdo:Plaintextnumpy
pandas
scikit-learn
joblib
▶️ ExecuçãoExecute o script principal:Bashpython beespace_mvp.py
Ao final da execução, o script deverá:Gerar uma base sintética;Treinar o modelo;Exibir métricas de avaliação;Listar as variáveis mais importantes;Simular a classificação de uma nova colmeia;Salvar o modelo treinado;Salvar a base sintética em CSV.📈 Saídas esperadasO terminal exibirá informações como:PlaintextAmostra dos dados:
...

Distribuição das classes:
normal     ...
atencao    ...
alerta     ...

Matriz de confusão:
...

Relatório de classificação:
...

Variáveis mais importantes para o modelo:
...

Classe prevista:
alerta
Também serão gerados dois arquivos:modelo_beespace_mvp.pkldados_sinteticos_beespace.csv💡 Exemplo de interpretaçãoUma colmeia pode ser classificada como alerta quando ocorre uma combinação de fatores como:Baixo NDVI;Baixa umidade da vegetação;Pouca chuva recente;Alta temperatura média;Baixa presença de mata nativa;Predominância agrícola;Queda de peso da colmeia;Baixa atividade das abelhas;Anomalia acústica;Mortalidade observada.Essa lógica representa a proposta central da BeeSpace: o satélite indica o contexto territorial, enquanto a colmeia valida o que está acontecendo no campo.⚠️ Limitações do MVPEste MVP é uma prova de conceito e possui limitações importantes:Os dados utilizados são sintéticos;Os rótulos das classes são gerados por regras simuladas;O modelo ainda não foi treinado com dados reais de sensores;A relação entre indicadores ambientais e saúde da colmeia precisa de validação em campo;Os indicadores de florada, biodiversidade e risco ambiental são aproximações iniciais;O uso de dados atmosféricos deve ser tratado como camada complementar até validação científica.⏭️ Próximos passosOs próximos passos recomendados são:Integrar dados reais do Copernicus Data Space Ecosystem.Automatizar recortes territoriais em raio de 3 km por colmeia.Calcular NDVI, EVI e NDWI a partir de imagens Sentinel-2.Incorporar dados climáticos ERA5-Land.Integrar leituras reais de sensores IoT.Coletar registros de campo com produtores.Validar rótulos com especialistas em apicultura, meliponicultura e sanidade.Re-treinar o modelo com dados reais.Criar um dashboard com mapas, indicadores e alertas.Evoluir o MVP para uma API de classificação em tempo quase real.🔄 Possível evolução técnicaUma evolução natural do MVP é separar o sistema em três modelos:ModeloFinalidadeClassificador de risco da colmeiaIdentificar colmeias em situação normal, atenção ou alertaEstimador de disponibilidade floralInferir potencial de pasto apícola a partir de vegetação, clima e dados da colmeiaDetector de anomalias ambientaisIdentificar padrões incomuns em regiões monitoradas🌐 Aplicação no projeto BeeSpaceEste MVP pode ser usado como base para:Demonstração técnica no hackathon;Validação da arquitetura de dados;Apresentação do pipeline Copernicus + colmeia inteligente;Geração de alertas simulados;Prototipação de dashboard;Explicação do papel da inteligência artificial na BeeSpace.🛑 Aviso sobre os dadosOs dados utilizados neste MVP são sintéticos e servem apenas para demonstrar o funcionamento do pipeline. Eles não devem ser interpretados como medições reais de colmeias, vegetação, clima, poluição ou biodiversidade.📄 LicençaDefinir a licença conforme a estratégia do projeto.Sugestão para projeto aberto: MIT License👥 AutoriaProjeto BeeSpace | CopernicusLAC Panamá Hackathon 2026MVP de Machine Learning para biovigilância ambiental com colmeias inteligentes e dados Copernicus.
