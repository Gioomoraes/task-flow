"""Leitura do arquivo CSV. Não interpreta o conteúdo dos campos."""

import csv

from taskflow.modelos import ErroDeArquivo, RegistroRejeitado

COLUNAS_OBRIGATORIAS = (
    "id",
    "titulo",
    "responsavel",
    "status",
    "prioridade",
    "data_criacao",
    "prazo",
    "data_conclusao",
)


def ler_csv(caminho):
    """Lê o arquivo e devolve (linhas, rejeitados).

    linhas: lista de (numero_linha, dicionario) com todos os campos em texto.
    rejeitados: linhas com número de colunas diferente do cabeçalho.
    Levanta ErroDeArquivo em caso de falha fatal.
    """
    linhas = []
    rejeitados = []

    try:
        with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)

            colunas = leitor.fieldnames
            if colunas is None:
                raise ErroDeArquivo("o arquivo está vazio.")
            faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in colunas]
            if faltando:
                raise ErroDeArquivo(
                    "faltam colunas obrigatórias: " + ", ".join(faltando) + "."
                )

            for linha in leitor:
                numero_linha = leitor.line_num
                # Colunas a mais vão para a chave None; a menos viram valor None.
                if None in linha or None in linha.values():
                    rejeitados.append(
                        RegistroRejeitado(
                            numero_linha,
                            ["número de colunas diferente do cabeçalho"],
                        )
                    )
                else:
                    linhas.append((numero_linha, linha))

    except FileNotFoundError:
        raise ErroDeArquivo(f"arquivo não encontrado: {caminho}")
    except IsADirectoryError:
        raise ErroDeArquivo(f"'{caminho}' é uma pasta, não um arquivo.")
    except PermissionError:
        raise ErroDeArquivo(
            f"sem permissão para ler '{caminho}' (ou o caminho é uma pasta)."
        )
    except UnicodeDecodeError:
        raise ErroDeArquivo("não foi possível decodificar o arquivo (esperado UTF-8).")
    except csv.Error as erro:
        raise ErroDeArquivo(f"o arquivo CSV está malformado: {erro}")
    except OSError as erro:
        raise ErroDeArquivo(f"não foi possível abrir o arquivo: {erro}")

    return linhas, rejeitados