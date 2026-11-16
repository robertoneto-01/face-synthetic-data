import argparse
from pathlib import Path
import sys

from functions import PROFILES, process_folder


def main():
    parser = argparse.ArgumentParser(description="Simula variações de captura em selfies com Pillow e NumPy.")
    parser.add_argument("entrada", type=Path, nargs="?", default=Path("dataset"), help="Pasta com as selfies originais, incluindo subpastas (padrão: dataset/).")
    parser.add_argument("saida", type=Path, nargs="?", default=Path("output"), help="Nova pasta para os JPEGs e o manifesto (padrão: output/).")
    parser.add_argument("--perfil", choices=("misto", *PROFILES), default="misto")
    parser.add_argument("--variantes", type=int, default=3, help="Número de saídas por entrada (padrão: 3).")
    parser.add_argument("--seed", type=int, default=42, help="Semente dos parâmetros e do ruído (padrão: 42).")
    args = parser.parse_args()
    if args.variantes < 1:
        parser.error("--variantes precisa ser maior ou igual a 1.")
    try:
        count = process_folder(
            args.entrada.resolve(), args.saida.resolve(), args.perfil, args.variantes, args.seed
        )
    except (OSError, ValueError) as error:
        parser.exit(1, f"Erro: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "Processamento interrompido.\n")
    print(f"{count} originais → {count * args.variantes} JPEGs em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
