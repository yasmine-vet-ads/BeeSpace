""" BeeSpace - Detecção de anomalias para colmeias inteligentes.

Este script treina um modelo não supervisionado para aprender o comportamento
normal de uma colmeia instrumentada com ESP32-S3 e telemetria MQTT/JSON.

Uso rápido no terminal:

    python firmware/esp32-s3/IA.py

Saída esperada:
- Geração de dados sintéticos de 30 dias.
- Treinamento de Isolation Forest usando somente janelas normais.
- Demonstração de inferência em payloads de teste.
- Exportação do artefato ``modelo_beespace_isolation_forest.pkl``.

Observação de arquitetura:
O ESP32-S3 continua apenas publicando sensores via MQTT. Este arquivo deve rodar
em um gateway, servidor local, backend cloud ou notebook de operação apícola.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# Caminho padrão do modelo exportado. Mantido ao lado do script para facilitar
# implantação em um gateway que consome MQTT e chama analisar_telemetria().
DEFAULT_MODEL_PATH = Path(__file__).with_name("modelo_beespace_isolation_forest.pkl")
RANDOM_SEED = 42


RAW_FEATURES: list[str] = [
    "temperature_c",
    "humidity_percent",
    "pressure_hpa",
    "luminosity_lux",
    "audio_rms",
    "audio_peak",
    "audio_zero_crossing_rate",
    "weight_kg",
    "bee_entries_per_min",
    "bee_exits_per_min",
]

ENGINEERED_FEATURES: list[str] = [
    "bee_flow_balance",
    "weight_delta_1h",
    "temperature_delta_1h",
    "acoustic_stress_index",
]

MODEL_FEATURES: list[str] = RAW_FEATURES + ENGINEERED_FEATURES


@dataclass(frozen=True)
class TelemetryModelBundle:
    """Artefato serializável necessário para inferência em produção.

    Attributes:
        scaler: Padronizador treinado no comportamento normal da colmeia.
        model: Isolation Forest treinado nas features padronizadas.
        feature_names: Ordem exata das colunas usadas pelo modelo.
        normal_profile: Estatísticas de referência para explicar desvios.
        contamination: Proporção esperada de anomalias durante treinamento.
    """

    scaler: StandardScaler
    model: IsolationForest
    feature_names: list[str]
    normal_profile: dict[str, dict[str, float]]
    contamination: float


def _daily_activity_factor(index: pd.DatetimeIndex) -> np.ndarray:
    """Retorna fator dia/noite para simular forrageamento das abelhas.

    Abelhas melíferas têm maior fluxo durante horas claras e queda acentuada à
    noite. O fator suaviza o nascer/pôr do sol para evitar dados artificiais
    com degraus bruscos.
    """

    hour = index.hour + index.minute / 60.0
    daylight = np.clip(np.sin((hour - 6.0) / 12.0 * np.pi), 0.0, None)
    return daylight.astype(float)


def gerar_dataset_sintetico(
    dias: int = 30,
    freq: str = "15min",
    seed: int = RANDOM_SEED,
    incluir_anomalias: bool = True,
) -> pd.DataFrame:
    """Gera séries temporais sintéticas de uma colmeia BeeSpace.

    O comportamento normal incorpora regras biológicas simplificadas:
    - Temperatura interna tende a ficar regulada perto de 34-35 °C.
    - Umidade varia lentamente e pode subir durante madrugada.
    - Peso aumenta gradualmente por entrada de néctar, com pequenas oscilações
      diárias por consumo interno e saída/entrada de campeiras.
    - Fluxo de abelhas é alto de dia e baixo de noite.
    - Zumbido normal fica estável; alterações acústicas fortes podem indicar
      estresse, ausência de rainha, ventilação intensa ou distúrbio estrutural.

    Também injeta anomalias rotuladas apenas para validação/demonstração. O
    modelo não usa esses rótulos no treinamento não supervisionado.
    """

    rng = np.random.default_rng(seed)
    periods = int(pd.Timedelta(days=dias) / pd.Timedelta(freq))
    timestamp = pd.date_range("2026-05-01", periods=periods, freq=freq)
    daylight = _daily_activity_factor(timestamp)
    hour = timestamp.hour + timestamp.minute / 60.0
    day_wave = np.sin(2.0 * np.pi * hour / 24.0)
    slow_weather_wave = np.sin(np.linspace(0.0, 4.0 * np.pi, periods))

    # Ambiente interno: a colmeia regula temperatura, mas sofre influência leve
    # do ciclo externo. Valores foram escolhidos como plausíveis para simulação,
    # não como limiares veterinários universais.
    temperature_c = 34.4 + 0.45 * day_wave + 0.25 * slow_weather_wave + rng.normal(0, 0.18, periods)
    humidity_percent = 57.0 - 4.0 * day_wave + 2.0 * slow_weather_wave + rng.normal(0, 1.4, periods)
    pressure_hpa = 1014.0 + 5.0 * np.sin(np.linspace(0.0, 3.0 * np.pi, periods)) + rng.normal(0, 0.7, periods)
    luminosity_lux = 20.0 + 8200.0 * daylight + rng.normal(0, 120.0, periods)
    luminosity_lux = np.clip(luminosity_lux, 0.0, None)

    # Acústica: RMS e pico sobem discretamente no período de maior atividade.
    audio_rms = 0.18 + 0.05 * daylight + rng.normal(0, 0.015, periods)
    audio_peak = 0.58 + 0.14 * daylight + rng.normal(0, 0.035, periods)
    audio_zero_crossing_rate = 0.105 + 0.018 * daylight + rng.normal(0, 0.006, periods)

    # Fluxo da catraca: entradas/saídas por minuto acompanham luz e clima.
    entries = rng.poisson(lam=np.clip(2.0 + 42.0 * daylight, 0.1, None)).astype(float)
    exits = rng.poisson(lam=np.clip(1.8 + 40.0 * daylight, 0.1, None)).astype(float)

    # Peso: tendência positiva lenta por néctar + oscilação intradiária.
    net_gain_per_step = 0.004 + 0.014 * daylight + rng.normal(0, 0.01, periods)
    weight_kg = 36.0 + np.cumsum(net_gain_per_step)
    weight_kg += 0.25 * np.sin(2.0 * np.pi * hour / 24.0 + np.pi) + rng.normal(0, 0.04, periods)

    df = pd.DataFrame(
        {
            "timestamp": timestamp,
            "temperature_c": temperature_c,
            "humidity_percent": humidity_percent,
            "pressure_hpa": pressure_hpa,
            "luminosity_lux": luminosity_lux,
            "audio_rms": audio_rms,
            "audio_peak": audio_peak,
            "audio_zero_crossing_rate": audio_zero_crossing_rate,
            "weight_kg": weight_kg,
            "bee_entries_per_min": entries,
            "bee_exits_per_min": exits,
            "anomaly_label": "normal",
        }
    )

    if incluir_anomalias:
        _injetar_anomalias_biologicas(df, rng)

    return adicionar_features_calculadas(df)


def _injetar_anomalias_biologicas(df: pd.DataFrame, rng: np.random.Generator) -> None:
    """Injeta cenários anômalos conhecidos para teste de negócio.

    Cenários simulados:
    1. Possível orfandade/estresse: queda de temperatura interna, aumento de
       instabilidade acústica e redução de fluxo.
    2. Possível enxameação: perda súbita de peso e pico de saídas.
    3. Possível falha estrutural/sensorial: umidade muito alta e alteração de
       luminosidade dentro da caixa.
    """

    # Janela de 8 horas: comportamento compatível com colmeia estressada ou órfã
    # de rainha, onde a termorregulação e o padrão acústico saem do basal.
    queenless_start = int(len(df) * 0.42)
    queenless_end = queenless_start + 32
    df.loc[queenless_start:queenless_end, "temperature_c"] -= rng.uniform(3.2, 4.6)
    df.loc[queenless_start:queenless_end, "audio_rms"] += rng.uniform(0.12, 0.18)
    df.loc[queenless_start:queenless_end, "audio_zero_crossing_rate"] += rng.uniform(0.05, 0.08)
    df.loc[queenless_start:queenless_end, "bee_entries_per_min"] *= 0.45
    df.loc[queenless_start:queenless_end, "bee_exits_per_min"] *= 0.65
    df.loc[queenless_start:queenless_end, "anomaly_label"] = "possivel_orfandade_ou_estresse"

    # Enxameação: muitas abelhas saem e o peso cai rapidamente em poucas janelas.
    swarm_start = int(len(df) * 0.68)
    swarm_end = swarm_start + 12
    drop = np.linspace(0.0, 5.8, swarm_end - swarm_start + 1)
    df.loc[swarm_start:swarm_end, "weight_kg"] -= drop
    df.loc[swarm_start:swarm_end, "bee_exits_per_min"] *= 2.8
    df.loc[swarm_start:swarm_end, "bee_entries_per_min"] *= 0.35
    df.loc[swarm_start:swarm_end, "audio_peak"] += 0.22
    df.loc[swarm_start:swarm_end, "anomaly_label"] = "possivel_enxameacao"

    # Falha física: infiltração/tampa deslocada/sensor exposto à luz.
    structure_start = int(len(df) * 0.82)
    structure_end = structure_start + 20
    df.loc[structure_start:structure_end, "humidity_percent"] += 22.0
    df.loc[structure_start:structure_end, "luminosity_lux"] += 4500.0
    df.loc[structure_start:structure_end, "temperature_c"] -= 1.4
    df.loc[structure_start:structure_end, "anomaly_label"] = "possivel_falha_estrutural"


def adicionar_features_calculadas(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona features de engenharia necessárias ao modelo.

    Features calculadas obrigatórias para negócio:
    - bee_flow_balance: entradas - saídas por minuto; saldo negativo persistente
      pode sinalizar enxameação, abandono, intoxicação ou perturbação.
    - weight_delta_1h: variação de peso na última hora; quedas abruptas são uma
      das assinaturas mais fortes de enxameação, queda de quadro ou furto.

    Features adicionais:
    - temperature_delta_1h: perda de termorregulação.
    - acoustic_stress_index: combinação simples de energia e cruzamento por zero.
    """

    enriched = df.copy()
    if "timestamp" in enriched.columns:
        enriched = enriched.sort_values("timestamp").reset_index(drop=True)

    enriched["bee_flow_balance"] = enriched["bee_entries_per_min"] - enriched["bee_exits_per_min"]

    # A frequência sintética padrão é 15 min; 4 passos equivalem a 1 hora. Em
    # produção, uma janela temporal real pode substituir essa aproximação.
    steps_1h = 4
    enriched["weight_delta_1h"] = enriched["weight_kg"].diff(periods=steps_1h)
    enriched["temperature_delta_1h"] = enriched["temperature_c"].diff(periods=steps_1h)
    enriched["acoustic_stress_index"] = (
        enriched["audio_rms"] * 2.0
        + enriched["audio_peak"] * 0.8
        + enriched["audio_zero_crossing_rate"] * 4.0
    )

    # Primeiras janelas não têm histórico suficiente; preencher com 0 representa
    # "sem variação conhecida" e evita descartar dados em tempo real.
    enriched[ENGINEERED_FEATURES] = enriched[ENGINEERED_FEATURES].fillna(0.0)
    return enriched


def treinar_modelo(
    df: pd.DataFrame,
    contamination: float = 0.03,
    random_state: int = RANDOM_SEED,
) -> TelemetryModelBundle:
    """Treina Isolation Forest no perfil normal da colmeia.

    O algoritmo é adequado para sensores IoT porque não requer rótulos de doença
    ou enxameação, funciona bem com múltiplas dimensões e retorna uma decisão de
    outlier por amostra. Para aprender o basal, removemos da simulação as linhas
    rotuladas como anômalas antes do ajuste.
    """

    missing = sorted(set(MODEL_FEATURES) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset sem features obrigatórias: {missing}")

    normal_df = df[df.get("anomaly_label", "normal") == "normal"].copy()
    if normal_df.empty:
        raise ValueError("Não há amostras normais suficientes para treinar o modelo.")

    scaler = StandardScaler()
    x_train = normal_df[MODEL_FEATURES].astype(float)
    x_train_scaled = scaler.fit_transform(x_train)

    model = IsolationForest(
        n_estimators=250,
        contamination=contamination,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(x_train_scaled)

    profile = {
        feature: {
            "mean": float(normal_df[feature].mean()),
            "std": float(normal_df[feature].std(ddof=0) or 1.0),
            "p05": float(normal_df[feature].quantile(0.05)),
            "p95": float(normal_df[feature].quantile(0.95)),
        }
        for feature in MODEL_FEATURES
    }

    return TelemetryModelBundle(
        scaler=scaler,
        model=model,
        feature_names=MODEL_FEATURES.copy(),
        normal_profile=profile,
        contamination=contamination,
    )


def salvar_modelo(bundle: TelemetryModelBundle, caminho: Path | str = DEFAULT_MODEL_PATH) -> Path:
    """Exporta o modelo treinado em formato joblib/pkl."""

    path = Path(caminho)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    return path


def carregar_modelo(caminho: Path | str = DEFAULT_MODEL_PATH) -> TelemetryModelBundle:
    """Carrega o artefato salvo para uso em servidor de produção."""

    return joblib.load(Path(caminho))


def _as_mapping(payload: str | bytes | Mapping[str, Any]) -> Mapping[str, Any]:
    """Normaliza payload MQTT recebido como JSON string, bytes ou dict."""

    if isinstance(payload, bytes):
        return json.loads(payload.decode("utf-8"))
    if isinstance(payload, str):
        return json.loads(payload)
    return payload


def _get_nested_number(
    payload: Mapping[str, Any],
    paths: Sequence[tuple[str, ...]],
    default: float = 0.0,
) -> float:
    """Obtém número de caminhos alternativos em JSONs MQTT heterogêneos."""

    for path in paths:
        current: Any = payload
        for key in path:
            if not isinstance(current, Mapping) or key not in current:
                current = None
                break
            current = current[key]
        if current is not None:
            return float(current)
    return default


def payload_para_dataframe(novo_payload_json: str | bytes | Mapping[str, Any]) -> pd.DataFrame:
    """Converte um payload MQTT/JSON em uma linha com as features esperadas.

    Aceita nomes flexíveis para facilitar integração com firmware e protótipos:
    ``environment.temperature_c`` ou ``environment.temperature``; ``scale.weight_kg``
    ou ``scale.weight``; ``bee_counter.entries_per_min`` ou ``bee_counter.in``.

    Para features de variação de última hora, o payload pode enviar contexto em
    ``history_1h`` com ``weight_kg`` e ``temperature_c``. Quando esse contexto não
    existe, a função assume variação 0 e deixa a decisão focada nos sensores
    instantâneos.
    """

    payload = _as_mapping(novo_payload_json)
    environment = payload.get("environment", {}) if isinstance(payload.get("environment", {}), Mapping) else {}
    timestamp = payload.get("timestamp") or pd.Timestamp.utcnow().isoformat()

    row: dict[str, Any] = {
        "timestamp": pd.to_datetime(timestamp, utc=True, errors="coerce"),
        "temperature_c": _get_nested_number(payload, [("environment", "temperature_c"), ("environment", "temperature"), ("temperature_c",)]),
        "humidity_percent": _get_nested_number(payload, [("environment", "humidity_percent"), ("environment", "humidity"), ("humidity_percent",)]),
        "pressure_hpa": _get_nested_number(payload, [("environment", "pressure_hpa"), ("environment", "pressure"), ("pressure_hpa",)], 1013.25),
        "luminosity_lux": _get_nested_number(payload, [("environment", "luminosity_lux"), ("environment", "luminosity"), ("luminosity_lux",)]),
        "audio_rms": _get_nested_number(payload, [("audio", "rms"), ("audio", "audio_rms"), ("audio_rms",)]),
        "audio_peak": _get_nested_number(payload, [("audio", "peak"), ("audio", "audio_peak"), ("audio_peak",)]),
        "audio_zero_crossing_rate": _get_nested_number(payload, [("audio", "zero_crossing_rate"), ("audio", "zcr"), ("audio_zero_crossing_rate",)]),
        "weight_kg": _get_nested_number(payload, [("scale", "weight_kg"), ("scale", "weight"), ("weight_kg",)]),
        "bee_entries_per_min": _get_nested_number(payload, [("bee_counter", "entries_per_min"), ("bee_counter", "entries"), ("bee_counter", "in"), ("bee_entries_per_min",)]),
        "bee_exits_per_min": _get_nested_number(payload, [("bee_counter", "exits_per_min"), ("bee_counter", "exits"), ("bee_counter", "out"), ("bee_exits_per_min",)]),
    }

    df = pd.DataFrame([row])
    df = adicionar_features_calculadas(df)

    history_1h = payload.get("history_1h", {})
    if isinstance(history_1h, Mapping):
        previous_weight = history_1h.get("weight_kg")
        previous_temperature = history_1h.get("temperature_c")
        if previous_weight is not None:
            df.loc[0, "weight_delta_1h"] = df.loc[0, "weight_kg"] - float(previous_weight)
        if previous_temperature is not None:
            df.loc[0, "temperature_delta_1h"] = df.loc[0, "temperature_c"] - float(previous_temperature)

    # Caso extremo: se temperatura ausente vier como 0, tenta alias soltos que já
    # apareceram em protótipos de payload.
    if df.loc[0, "temperature_c"] == 0.0 and "temp" in environment:
        df.loc[0, "temperature_c"] = float(environment["temp"])

    return df


def _descrever_sensor(feature: str, value: float, profile: Mapping[str, Mapping[str, float]]) -> str:
    """Traduz o desvio numérico em uma explicação operacional."""

    stats = profile[feature]
    mean = stats["mean"]
    std = stats["std"] or 1.0
    z_score = (value - mean) / std
    direction = "acima" if z_score > 0 else "abaixo"

    business_meaning = {
        "temperature_c": "termorregulação interna alterada; pode indicar estresse, perda de população ou falha de vedação",
        "humidity_percent": "umidade fora do basal; pode sugerir ventilação inadequada, infiltração ou estresse térmico",
        "luminosity_lux": "luminosidade anormal dentro/ao redor da caixa; verificar tampa, frestas ou exposição do sensor",
        "audio_rms": "energia acústica atípica; pode indicar agitação, ventilação intensa ou perturbação",
        "audio_peak": "picos acústicos incomuns; pode indicar ruído impulsivo, manejo ou estresse",
        "audio_zero_crossing_rate": "frequência/zumbido alterado; observar possível orfandade de rainha ou agitação",
        "weight_kg": "peso total fora do padrão esperado para a colmeia",
        "bee_entries_per_min": "entradas fora do padrão para o horário/colmeia",
        "bee_exits_per_min": "saídas fora do padrão; pico pode acompanhar enxameação ou distúrbio",
        "bee_flow_balance": "saldo entradas-saídas desequilibrado; saída líquida elevada exige inspeção",
        "weight_delta_1h": "variação horária de peso anormal; queda brusca sugere enxameação, furto ou falha estrutural",
        "temperature_delta_1h": "mudança rápida de temperatura; risco de perda de termorregulação",
        "acoustic_stress_index": "índice acústico composto elevado; reforça hipótese de estresse biológico",
    }.get(feature, "sensor fora do perfil normal")

    return (
        f"{feature}={value:.3f} ({abs(z_score):.1f} desvios-padrão {direction} do normal): "
        f"{business_meaning}"
    )


def explicar_desvios(
    row: pd.Series,
    bundle: TelemetryModelBundle,
    limite_zscore: float = 2.0,
    max_sensores: int = 5,
) -> list[str]:
    """Lista os sensores/features que mais explicam uma anomalia."""

    deviations: list[tuple[float, str]] = []
    for feature in bundle.feature_names:
        value = float(row[feature])
        stats = bundle.normal_profile[feature]
        std = stats["std"] or 1.0
        z_score = (value - stats["mean"]) / std
        outside_percentile = value < stats["p05"] or value > stats["p95"]
        if abs(z_score) >= limite_zscore or outside_percentile:
            deviations.append((abs(z_score), _descrever_sensor(feature, value, bundle.normal_profile)))

    deviations.sort(key=lambda item: item[0], reverse=True)
    return [description for _, description in deviations[:max_sensores]]


def analisar_telemetria(
    novo_payload_json: str | bytes | Mapping[str, Any],
    modelo_path: Path | str = DEFAULT_MODEL_PATH,
    bundle: TelemetryModelBundle | None = None,
) -> str | None:
    """Analisa telemetria em tempo real e retorna alerta textual se anômala.

    Args:
        novo_payload_json: Payload MQTT/JSON de uma leitura da colmeia.
        modelo_path: Caminho do .pkl gerado por salvar_modelo().
        bundle: Modelo já carregado em memória, útil para serviços long-running.

    Returns:
        Texto de alerta pronto para notificação, ou None quando a leitura está
        dentro do padrão aprendido.
    """

    loaded_bundle = bundle if bundle is not None else carregar_modelo(modelo_path)
    row_df = payload_para_dataframe(novo_payload_json)
    x = row_df[loaded_bundle.feature_names].astype(float)
    x_scaled = loaded_bundle.scaler.transform(x)

    prediction = int(loaded_bundle.model.predict(x_scaled)[0])
    anomaly_score = float(loaded_bundle.model.decision_function(x_scaled)[0])

    if prediction == 1:
        return None

    row = row_df.iloc[0]
    timestamp = row.get("timestamp", pd.Timestamp.utcnow())
    sensor_explanations = explicar_desvios(row, loaded_bundle)
    if not sensor_explanations:
        sensor_explanations = [
            "combinação multivariada rara: nenhum sensor isolado excedeu o limite, mas o conjunto saiu do padrão normal."
        ]

    alert_lines = [
        "🚨 ALERTA BeeSpace: anomalia detectada na colmeia inteligente.",
        f"Horário da leitura: {timestamp}",
        f"Score Isolation Forest: {anomaly_score:.4f} (valores menores indicam maior anomalia).",
        "Sensores/features que mais contribuíram para o desvio:",
    ]
    alert_lines.extend(f"- {description}" for description in sensor_explanations)
    alert_lines.append(
        "Ação recomendada: confirmar no dashboard, verificar histórico das últimas horas e priorizar inspeção de campo se o alerta persistir."
    )
    return "\n".join(alert_lines)


def _payload_demo_normal() -> dict[str, Any]:
    """Payload normal para demonstração rápida da função de inferência."""

    return {
        "timestamp": "2026-05-31T10:15:00Z",
        "environment": {
            "temperature_c": 34.7,
            "humidity_percent": 55.0,
            "pressure_hpa": 1015.0,
            "luminosity_lux": 7600.0,
        },
        "audio": {"rms": 0.22, "peak": 0.70, "zero_crossing_rate": 0.12},
        "scale": {"weight_kg": 40.8},
        "bee_counter": {"entries_per_min": 39, "exits_per_min": 37},
        "history_1h": {"weight_kg": 40.7, "temperature_c": 34.6},
    }


def _payload_demo_anomalo() -> dict[str, Any]:
    """Payload anômalo simulando queda de peso + fluxo de saída elevado."""

    return {
        "timestamp": "2026-05-31T11:00:00Z",
        "environment": {
            "temperature_c": 31.0,
            "humidity_percent": 61.0,
            "pressure_hpa": 1014.2,
            "luminosity_lux": 7900.0,
        },
        "audio": {"rms": 0.39, "peak": 0.93, "zero_crossing_rate": 0.19},
        "scale": {"weight_kg": 35.2},
        "bee_counter": {"entries_per_min": 12, "exits_per_min": 105},
        "history_1h": {"weight_kg": 40.9, "temperature_c": 34.5},
    }


def main() -> None:
    """Executa pipeline completo: simulação, treinamento, teste e exportação."""

    print("🐝 Gerando dataset sintético BeeSpace de 30 dias...")
    df = gerar_dataset_sintetico()
    print(f"Amostras geradas: {len(df)}")
    print("Distribuição dos rótulos sintéticos de validação:")
    print(df["anomaly_label"].value_counts().to_string())

    print("\n🧠 Treinando Isolation Forest com janelas normais...")
    bundle = treinar_modelo(df)

    x_all = bundle.scaler.transform(df[bundle.feature_names].astype(float))
    df["predicao"] = bundle.model.predict(x_all)
    detected = int((df["predicao"] == -1).sum())
    print(f"Janelas sinalizadas como anômalas no dataset completo: {detected}")

    output_path = salvar_modelo(bundle)
    print(f"\n💾 Modelo exportado em: {output_path}")

    print("\n🔎 Demonstração com payload normal:")
    normal_alert = analisar_telemetria(_payload_demo_normal(), bundle=bundle)
    print(normal_alert or "✅ Telemetria normal: nenhum alerta gerado.")

    print("\n🔎 Demonstração com payload anômalo:")
    anomalous_alert = analisar_telemetria(_payload_demo_anomalo(), bundle=bundle)
    print(anomalous_alert or "✅ Telemetria normal: nenhum alerta gerado.")


if __name__ == "__main__":
    main()
