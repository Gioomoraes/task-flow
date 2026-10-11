"""Ponto de entrada: python -m taskflow caminho/do/arquivo.csv"""

import argparse
import sys

from taskflow.leitor_csv import ler_csv
from taskflow.modelos import ErroDeArquivo
from taskflow.validacao import validar_linhas


def main():
    parser = argparse.ArgumentParser(
        description="Analisa um arquivo CSV de tarefas operacionais."
    )
    parser.add_argument("caminho", help="caminho do arquivo CSV")
    args = parser.parse_args()

    try:
        linhas, rejeitados_leitura = ler_csv(args.caminho)
    except ErroDeArquivo as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    tarefas, rejeitados_validacao = validar_linhas(linhas)
    rejeitados = rejeitados_leitura + rejeitados_validacao
    rejeitados.sort(key=lambda registro: registro.numero_linha)

    # Saída provisória, para acompanhar a fase. O relatório virá depois.
    total = len(tarefas) + len(rejeitados)
    print(f"Linhas lidas: {total} | Válidas: {len(tarefas)} | Inválidas: {len(rejeitados)}")
    for registro in rejeitados:
        print(f"  linha {registro.numero_linha}: " + "; ".join(registro.erros))

    return 0


if __name__ == "__main__":
    sys.exit(main())