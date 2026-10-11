"""Ponto de entrada: python -m taskflow caminho/do/arquivo.csv"""

import argparse
import sys
from datetime import date

from taskflow.leitor_csv import ler_csv
from taskflow.modelos import ErroDeArquivo
from taskflow.regras import dias_de_atraso
from taskflow.validacao import converter_data, separar_duplicadas, validar_linhas


def data_iso(texto):
    """Converte o argumento da linha de comando em date, para o argparse."""
    try:
        return converter_data(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"data inválida: {texto!r} (use AAAA-MM-DD)"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Analisa um arquivo CSV de tarefas operacionais."
    )
    parser.add_argument("caminho", help="caminho do arquivo CSV")
    parser.add_argument(
        "--data-referencia",
        type=data_iso,
        default=None,
        help="data usada para decidir atrasos, AAAA-MM-DD (padrão: hoje)",
    )
    args = parser.parse_args()
    data_referencia = args.data_referencia or date.today()

    try:
        linhas, rejeitados_leitura = ler_csv(args.caminho)
    except ErroDeArquivo as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    validas, rejeitados_validacao = validar_linhas(linhas)
    unicas, duplicadas = separar_duplicadas(validas)

    rejeitados = rejeitados_leitura + rejeitados_validacao
    rejeitados.sort(key=lambda registro: registro.numero_linha)

    atrasadas = []
    for tarefa in unicas:
        dias = dias_de_atraso(tarefa, data_referencia)
        if dias > 0:
            atrasadas.append((tarefa, dias))
    # Mais atrasada primeiro; em empate, menor id primeiro.
    atrasadas.sort(key=lambda par: (-par[1], par[0].id))

    # Saída provisória, para acompanhar a fase. O relatório virá depois.
    total = len(unicas) + len(rejeitados) + len(duplicadas)
    print(f"Data de referência: {data_referencia}")
    print(
        f"Linhas lidas: {total} | Únicas: {len(unicas)} | "
        f"Rejeitadas: {len(rejeitados)} | Duplicadas: {len(duplicadas)}"
    )
    print(f"Atrasadas: {len(atrasadas)}")
    for tarefa, dias in atrasadas:
        unidade = "dia" if dias == 1 else "dias"
        print(
            f"  #{tarefa.id}  {tarefa.titulo}  ({tarefa.responsavel})  "
            f"prazo {tarefa.prazo}  [{dias} {unidade}]"
        )
    if rejeitados:
        print("Rejeitadas:")
        for registro in rejeitados:
            print(f"  linha {registro.numero_linha}: " + "; ".join(registro.erros))
    if duplicadas:
        print("Duplicadas:")
        for registro in duplicadas:
            print(f"  linha {registro.numero_linha}: " + "; ".join(registro.erros))

    return 0


if __name__ == "__main__":
    sys.exit(main())