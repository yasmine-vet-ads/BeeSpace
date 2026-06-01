"""Módulo de Visão Computacional do BeeSpace.

Este script executa o pipeline de inferência para fotos de favos de mel usando um
modelo YOLO treinado no Roboflow. O objetivo é transformar detecções de alvéolos
em um laudo quantitativo com contagens, percentuais, imagem anotada e gráfico de
distribuição.

Exemplo de uso:
    python CODIGO.ML.VC.py --model best.pt --image exemplos/favo.jpg --output-dir saidas
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Mapping, Optional


# Classes esperadas no dataset Roboflow/YOLO do BeeSpace.
BEE_CLASSES: tuple[str, ...] = (
    "mel",
    "nectar",
    "polen",
    "ovos",
    "larvas",
    "crias_operculadas",
)

# Paleta estável para manter consistência visual entre relatórios.
CLASS_COLORS: dict[str, str] = {
    "mel": "#F9C74F",
    "nectar": "#90BE6D",
    "polen": "#F8961E",
    "ovos": "#F8F9FA",
    "larvas": "#43AA8B",
    "crias_operculadas": "#8D6E63",
}

logger = logging.getLogger(__name__)


def load_yolo_model(model_path: str | Path) -> Any:
    """Carrega um modelo YOLO treinado a partir de um arquivo ``.pt``.

    Args:
        model_path: Caminho para o peso treinado, normalmente ``best.pt``
            exportado pelo treinamento YOLO/Roboflow.

    Returns:
        Instância do modelo YOLO pronta para inferência.

    Raises:
        FileNotFoundError: Se o arquivo de pesos não existir.
        RuntimeError: Se a biblioteca Ultralytics não conseguir carregar o modelo.
    """
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"Modelo YOLO não encontrado: {path}")

    from ultralytics import YOLO

    try:
        model = YOLO(str(path))
    except Exception as exc:  # noqa: BLE001 - adiciona contexto operacional ao erro.
        raise RuntimeError(f"Falha ao carregar o modelo YOLO em {path}: {exc}") from exc

    logger.info("Modelo YOLO carregado com sucesso: %s", path)
    return model


def run_inference(
    model: Any,
    image_path: str | Path,
    confidence_threshold: float = 0.25,
    image_size: int = 1024,
) -> tuple[dict[str, int], object]:
    """Executa inferência YOLO em uma foto de favo e conta as detecções por classe.

    Args:
        model: Modelo YOLO já carregado.
        image_path: Caminho da imagem do favo capturada pelo apicultor.
        confidence_threshold: Confiança mínima para aceitar uma bounding box.
        image_size: Tamanho de inferência usado pelo YOLO.

    Returns:
        Tupla contendo um dicionário ``{classe: contagem}`` e o objeto de resultado
        da Ultralytics, usado posteriormente para renderizar as bounding boxes.

    Raises:
        FileNotFoundError: Se a imagem não existir.
        ValueError: Se a imagem não puder ser decodificada pelo OpenCV.
        RuntimeError: Se a inferência falhar ou não retornar resultados.
    """
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Imagem do favo não encontrada: {path}")

    import cv2

    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"OpenCV não conseguiu ler a imagem: {path}")

    counts = {class_name: 0 for class_name in BEE_CLASSES}

    try:
        results = model.predict(
            source=image,
            conf=confidence_threshold,
            imgsz=image_size,
            verbose=False,
        )
    except Exception as exc:  # noqa: BLE001 - preserva stack trace com mensagem de domínio.
        raise RuntimeError(f"Falha durante a inferência YOLO: {exc}") from exc

    if not results:
        raise RuntimeError("A inferência YOLO não retornou resultados.")

    result = results[0]
    class_id_to_name = result.names

    if result.boxes is not None and result.boxes.cls is not None:
        detected_class_ids = result.boxes.cls.cpu().numpy().astype(int)
        for class_id in detected_class_ids:
            class_name = str(class_id_to_name.get(class_id, class_id)).strip()
            if class_name in counts:
                counts[class_name] += 1
            else:
                logger.warning(
                    "Classe detectada não mapeada no BeeSpace: id=%s, nome=%s",
                    class_id,
                    class_name,
                )

    logger.info("Inferência concluída para %s: %s", path, counts)
    return counts, result


def calculate_honeycomb_composition(counts: Mapping[str, int]) -> Any:
    """Converte contagens absolutas em percentuais de composição do favo.

    Args:
        counts: Mapeamento entre classe e número de bounding boxes detectadas.

    Returns:
        DataFrame com as colunas ``classe``, ``contagem`` e ``percentual``.
        Quando nenhuma detecção é encontrada, todos os percentuais são ``0.0``.

    Raises:
        ValueError: Se alguma contagem for negativa.
    """
    import pandas as pd

    normalized_counts = {class_name: int(counts.get(class_name, 0)) for class_name in BEE_CLASSES}

    if any(value < 0 for value in normalized_counts.values()):
        raise ValueError("As contagens de detecção não podem ser negativas.")

    total = sum(normalized_counts.values())
    rows = []
    for class_name in BEE_CLASSES:
        count = normalized_counts[class_name]
        percentage = (count / total * 100.0) if total else 0.0
        rows.append(
            {
                "classe": class_name,
                "contagem": count,
                "percentual": round(percentage, 2),
            }
        )

    return pd.DataFrame(rows)


def save_distribution_chart(
    composition_df: Any,
    output_path: str | Path,
    title: str = "Composição percentual do favo",
) -> Path:
    """Gera e salva um gráfico de barras horizontais da distribuição do favo.

    Args:
        composition_df: DataFrame produzido por ``calculate_honeycomb_composition``.
        output_path: Caminho onde a imagem do gráfico será salva.
        title: Título exibido no gráfico.

    Returns:
        Caminho final do arquivo de gráfico salvo.

    Raises:
        ValueError: Se o DataFrame não contiver as colunas necessárias.
    """
    required_columns = {"classe", "contagem", "percentual"}
    if not required_columns.issubset(composition_df.columns):
        raise ValueError(f"DataFrame deve conter as colunas: {sorted(required_columns)}")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    plot_df = composition_df.sort_values("percentual", ascending=True).copy()
    colors = [CLASS_COLORS.get(class_name, "#577590") for class_name in plot_df["classe"]]

    import matplotlib.pyplot as plt

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    bars = ax.barh(plot_df["classe"], plot_df["percentual"], color=colors, edgecolor="#263238")

    ax.set_title(title, fontsize=17, fontweight="bold", pad=16)
    ax.set_xlabel("Percentual das detecções (%)", fontsize=12)
    ax.set_ylabel("Classe apícola", fontsize=12)
    ax.set_xlim(0, max(100, float(plot_df["percentual"].max()) + 10))

    for bar, (_, row) in zip(bars, plot_df.iterrows()):
        width = bar.get_width()
        ax.text(
            width + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{row['percentual']:.2f}% ({int(row['contagem'])})",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    fig.text(
        0.99,
        0.01,
        "BeeSpace • Visão Computacional para Manejo Inteligente",
        ha="right",
        va="bottom",
        fontsize=9,
        color="#546E7A",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)

    logger.info("Gráfico de distribuição salvo em: %s", output)
    return output


def save_annotated_image(result: object, output_path: str | Path) -> Path:
    """Salva a imagem de inferência com bounding boxes desenhadas pelo YOLO.

    Args:
        result: Resultado individual retornado pela Ultralytics.
        output_path: Caminho final da imagem anotada.

    Returns:
        Caminho da imagem anotada salva.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    import cv2

    annotated_image = result.plot()
    success = cv2.imwrite(str(output), annotated_image)
    if not success:
        raise RuntimeError(f"Não foi possível salvar a imagem anotada em: {output}")

    logger.info("Imagem com bounding boxes salva em: %s", output)
    return output


def export_composition_csv(composition_df: Any, output_path: str | Path) -> Path:
    """Exporta o laudo quantitativo tabular em CSV para integração com dashboards.

    Args:
        composition_df: DataFrame com contagens e percentuais por classe.
        output_path: Caminho de saída do arquivo CSV.

    Returns:
        Caminho do CSV salvo.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    composition_df.to_csv(output, index=False, encoding="utf-8")
    logger.info("Laudo quantitativo CSV salvo em: %s", output)
    return output


def process_honeycomb_image(
    model_path: str | Path,
    image_path: str | Path,
    output_dir: str | Path = "outputs",
    confidence_threshold: float = 0.25,
    image_size: int = 1024,
) -> dict[str, Any]:
    """Orquestra o pipeline completo: modelo, inferência, imagem anotada e gráfico.

    Args:
        model_path: Caminho para ``best.pt``.
        image_path: Caminho da foto do favo.
        output_dir: Diretório onde os artefatos serão salvos.
        confidence_threshold: Confiança mínima das detecções.
        image_size: Tamanho de inferência do YOLO.

    Returns:
        Dicionário com caminhos dos artefatos gerados e o DataFrame de composição.
    """
    model = load_yolo_model(model_path)
    counts, result = run_inference(
        model=model,
        image_path=image_path,
        confidence_threshold=confidence_threshold,
        image_size=image_size,
    )
    composition_df = calculate_honeycomb_composition(counts)

    output_base = Path(output_dir)
    image_stem = Path(image_path).stem
    annotated_path = output_base / f"{image_stem}_bounding_boxes.jpg"
    chart_path = output_base / f"{image_stem}_laudo_percentual.png"
    csv_path = output_base / f"{image_stem}_laudo_quantitativo.csv"

    save_annotated_image(result, annotated_path)
    save_distribution_chart(composition_df, chart_path)
    export_composition_csv(composition_df, csv_path)

    return {
        "annotated_image": annotated_path,
        "chart": chart_path,
        "csv": csv_path,
        "composition": composition_df,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    """Cria o parser de argumentos de linha de comando do módulo."""
    parser = argparse.ArgumentParser(
        description="Pipeline BeeSpace de Visão Computacional para análise de favos.",
    )
    parser.add_argument("--model", required=True, help="Caminho para o peso YOLO treinado (best.pt).")
    parser.add_argument("--image", required=True, help="Caminho para a imagem do favo de mel.")
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Diretório para salvar imagem anotada, gráfico e CSV. Padrão: outputs.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confiança mínima para aceitar detecções. Padrão: 0.25.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=1024,
        help="Tamanho de inferência do YOLO. Padrão: 1024.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Nível de log. Padrão: INFO.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Executa o pipeline pela linha de comando.

    Args:
        argv: Lista opcional de argumentos. Quando ``None``, usa ``sys.argv``.

    Returns:
        Código de saída do processo: ``0`` em sucesso e ``1`` em falha tratada.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        artifacts = process_honeycomb_image(
            model_path=args.model,
            image_path=args.image,
            output_dir=args.output_dir,
            confidence_threshold=args.conf,
            image_size=args.imgsz,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        logger.error("Pipeline interrompido: %s", exc)
        return 1

    composition_df = artifacts["composition"]
    print("\n=== Laudo Quantitativo BeeSpace ===")
    print(composition_df.to_string(index=False))
    print("\nArtefatos gerados:")
    print(f"- Imagem anotada: {artifacts['annotated_image']}")
    print(f"- Gráfico percentual: {artifacts['chart']}")
    print(f"- CSV quantitativo: {artifacts['csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
