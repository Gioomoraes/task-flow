"""Estruturas de dados e exceções compartilhadas pelo TaskFlow."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Tarefa:
    """Uma tarefa válida, já com os tipos corretos."""

    numero_linha: int
    id: int
    titulo: str
    responsavel: str
    status: str
    prioridade: str
    data_criacao: date
    prazo: date
    data_conclusao: date | None


@dataclass
class RegistroRejeitado:
    """Uma linha do CSV que não pôde ser aceita, com todos os motivos."""

    numero_linha: int
    erros: list[str]


class ErroDeArquivo(Exception):
    """Falha fatal: não é possível produzir um relatório confiável."""