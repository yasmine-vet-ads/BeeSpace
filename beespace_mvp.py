# MVP BeeSpace
# Classificação de risco ambiental, produtivo e sanitário por colmeia inteligente
# Prova de conceito com dados sintéticos
#
# Projeto: BeeSpace
# Contexto: CopernicusLAC Panamá Hackathon 2026
#
# Este script demonstra como dados macroambientais, como vegetação,
# clima, cobertura do solo e atmosfera, podem ser combinados com dados
# locais de uma colmeia inteligente para classificar o nível de risco
# de uma área monitorada.

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance

import joblib


RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


def gerar_dados_sinteticos(n=1500):
    """
    Gera uma base sintética para simular a integração entre:
    dados Copernicus, sensores IoT, visão computacional, bioacústica
    e registros de campo.

    Cada linha representa uma colmeia inteligente em determinado período.

    Os dados são sintéticos e servem apenas para prova de conceito.
    """

    dados = pd.DataFrame({
        # Dados Copernicus e ambientais
        # Sentinel-2 / CLMS
        "ndvi": np.random.uniform(0.15, 0.85, n),
        "evi": np.random.uniform(0.10, 0.75, n),
        "ndwi": np.random.uniform(-0.30, 0.55, n),

        # C3S / ERA5-Land
        "temp_media": np.random.uniform(10, 40, n),
        "precipitacao_7d": np.random.uniform(0, 120, n),
        "umidade_solo": np.random.uniform(0.05, 0.70, n),

        # Sentinel-5P / CAMS, representado como índice sintético
        "poluicao_indice": np.random.uniform(0, 1, n),

        # CLMS Land Cover, proporções no raio de 3 km
        "perc_mata_nativa": np.random.uniform(0, 1, n),
        "perc_agricultura": np.random.uniform(0, 1, n),
        "perc_solo_exposto": np.random.uniform(0, 0.7, n),

        # Dados locais da colmeia inteligente
        "temp_colmeia": np.random.uniform(25, 42, n),
        "umidade_colmeia": np.random.uniform(35, 85, n),
        "variacao_peso_7d": np.random.uniform(-4, 5, n),
        "atividade_abelhas": np.random.uniform(0, 1, n),
        "anomalia_acustica": np.random.uniform(0, 1, n),
        "mortalidade_observada": np.random.uniform(0, 1, n),
    })

    # Normalização simples das proporções de cobertura e uso do solo.
    # A soma das três proporções passa a representar 100% do recorte analisado.
    soma = (
        dados["perc_mata_nativa"]
        + dados["perc_agricultura"]
        + dados["perc_solo_exposto"]
    )

    dados["perc_mata_nativa"] = dados["perc_mata_nativa"] / soma
    dados["perc_agricultura"] = dados["perc_agricultura"] / soma
    dados["perc_solo_exposto"] = dados["perc_solo_exposto"] / soma

    # Regra de rotulagem sintética.
    # Esta regra cria o "gabarito" inicial para treinar o modelo.
    # Em uma versão real, estes rótulos seriam validados em campo por especialistas,
    # produtores, sensores reais e registros históricos.

    score_risco = (
        (dados["ndvi"] < 0.35).astype(int) * 2
        + (dados["evi"] < 0.25).astype(int) * 1
        + (dados["ndwi"] < 0.00).astype(int) * 1
        + (dados["precipitacao_7d"] < 15).astype(int) * 1
        + (dados["umidade_solo"] < 0.20).astype(int) * 1
        + (dados["temp_media"] > 33).astype(int) * 1
        + (dados["temp_colmeia"] > 37).astype(int) * 2
        + (dados["umidade_colmeia"] < 45).astype(int) * 1
        + (dados["variacao_peso_7d"] < -1.0).astype(int) * 2
        + (dados["atividade_abelhas"] < 0.35).astype(int) * 2
        + (dados["anomalia_acustica"] > 0.65).astype(int) * 2
        + (dados["mortalidade_observada"] > 0.55).astype(int) * 3
        + (dados["poluicao_indice"] > 0.70).astype(int) * 1
        + (dados["perc_agricultura"] > 0.60).astype(int) * 1
        + (dados["perc_solo_exposto"] > 0.25).astype(int) * 1
        + (dados["perc_mata_nativa"] < 0.20).astype(int) * 1
    )

    condicoes = [
        score_risco <= 3,
        (score_risco > 3) & (score_risco <= 7),
        score_risco > 7
    ]

    classes = ["normal", "atencao", "alerta"]

    dados["classe_risco"] = np.select(condicoes, classes)

    return dados


def treinar_modelo(dados):
    """
    Treina um classificador Random Forest para prever a classe de risco
    da colmeia monitorada.
    """

    X = dados.drop(columns=["classe_risco"])
    y = dados["classe_risco"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y
    )

    modelo = Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            random_state=RANDOM_STATE,
            class_weight="balanced"
        ))
    ])

    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    print("\nMatriz de confusão:")
    print(confusion_matrix(y_test, y_pred))

    print("\nRelatório de classificação:")
    print(classification_report(y_test, y_pred))

    return modelo, X_train, X_test, y_train, y_test


def explicar_modelo(modelo, X_test, y_test):
    """
    Calcula a importância das variáveis por permutação.

    Esta etapa ajuda a explicar quais variáveis mais influenciaram
    as previsões do modelo.
    """

    resultado = permutation_importance(
        modelo,
        X_test,
        y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring="accuracy"
    )

    importancia = pd.DataFrame({
        "variavel": X_test.columns,
        "importancia_media": resultado.importances_mean,
        "desvio": resultado.importances_std
    }).sort_values(by="importancia_media", ascending=False)

    return importancia


def prever_nova_colmeia(modelo):
    """
    Simula a entrada de uma nova colmeia inteligente.

    O exemplo representa um cenário de risco:
    baixo vigor vegetal, baixa chuva, predominância agrícola,
    queda de peso, baixa atividade, anomalia acústica e mortalidade.
    """

    nova_colmeia = pd.DataFrame([{
        # Dados Copernicus e ambientais
        "ndvi": 0.31,
        "evi": 0.28,
        "ndwi": -0.08,
        "temp_media": 34.5,
        "precipitacao_7d": 8.0,
        "umidade_solo": 0.16,
        "poluicao_indice": 0.74,

        # Cobertura e uso do solo
        "perc_mata_nativa": 0.15,
        "perc_agricultura": 0.72,
        "perc_solo_exposto": 0.13,

        # Dados da colmeia inteligente
        "temp_colmeia": 38.2,
        "umidade_colmeia": 42.0,
        "variacao_peso_7d": -2.4,
        "atividade_abelhas": 0.22,
        "anomalia_acustica": 0.81,
        "mortalidade_observada": 0.62,
    }])

    classe = modelo.predict(nova_colmeia)[0]
    probabilidades = modelo.predict_proba(nova_colmeia)[0]
    classes = modelo.named_steps["classifier"].classes_

    print("\nNova colmeia analisada:")
    print(nova_colmeia)

    print("\nClasse prevista:")
    print(classe)

    print("\nProbabilidades por classe:")
    for nome_classe, prob in zip(classes, probabilidades):
        print(f"{nome_classe}: {prob:.2%}")


def main():
    """
    Função principal do MVP BeeSpace.
    """

    print("Gerando dados sintéticos BeeSpace...")
    dados = gerar_dados_sinteticos(n=1500)

    print("\nAmostra dos dados:")
    print(dados.head())

    print("\nDistribuição das classes:")
    print(dados["classe_risco"].value_counts())

    print("\nTreinando modelo...")
    modelo, X_train, X_test, y_train, y_test = treinar_modelo(dados)

    print("\nCalculando importância das variáveis...")
    importancia = explicar_modelo(modelo, X_test, y_test)

    print("\nVariáveis mais importantes para o modelo:")
    print(importancia.head(10))

    print("\nSimulando previsão de nova colmeia...")
    prever_nova_colmeia(modelo)

    # Salvamento dos artefatos
    joblib.dump(modelo, "modelo_beespace_mvp.pkl")
    dados.to_csv("dados_sinteticos_beespace.csv", index=False)

    print("\nArquivos gerados:")
    print("modelo_beespace_mvp.pkl")
    print("dados_sinteticos_beespace.csv")

    print("\nExecução concluída com sucesso.")


if __name__ == "__main__":
    main()