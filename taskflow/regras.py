"""Regras de negócio do TaskFlow."""

STATUS_ENCERRADOS = ("concluida", "cancelada")


def dias_de_atraso(tarefa, data_referencia):
    """Devolve quantos dias a tarefa está atrasada (0 se não está).

    Atrasada = prazo anterior à data de referência E status não encerrado.
    Prazo igual à data de referência NÃO é atraso.
    """
    if tarefa.status in STATUS_ENCERRADOS:
        return 0
    return max((data_referencia - tarefa.prazo).days, 0)


def esta_atrasada(tarefa, data_referencia):
    """Verdadeiro se a tarefa está atrasada na data de referência."""
    return dias_de_atraso(tarefa, data_referencia) > 0