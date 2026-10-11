"""Cálculos e agrupamentos sobre as tarefas válidas e únicas.

Nenhuma função daqui imprime ou lê arquivos: recebem dados e devolvem dados.
"""

from taskflow.modelos import ResultadoAnalise, ResumoResponsavel
from taskflow.regras import dias_de_atraso, esta_atrasada, esta_em_aberto
from taskflow.validacao import PRIORIDADES_VALIDAS, STATUS_VALIDOS


def _contar_por(tarefas, atributo, valores):
    """Conta as tarefas segundo um atributo (por nome).

    Devolve um dicionário com todos os 'valores', na ordem dada, com 0
    quando não há tarefas. Um valor fora da lista levanta KeyError, de
    propósito: depois da validação isso seria um bug.
    """
    contagem = {valor: 0 for valor in valores}
    for tarefa in tarefas:
        contagem[getattr(tarefa, atributo)] += 1
    return contagem


def contar_por_status(tarefas):
    """Conta as tarefas por status (sempre os quatro, em ordem)."""
    return _contar_por(tarefas, "status", STATUS_VALIDOS)


def contar_por_prioridade(tarefas):
    """Conta as tarefas por prioridade (sempre as três, em ordem)."""
    return _contar_por(tarefas, "prioridade", PRIORIDADES_VALIDAS)


def resumir_por_responsavel(tarefas, data_referencia):
    """Resume as tarefas de cada responsável.

    Devolve uma lista de ResumoResponsavel, de quem tem mais tarefas para
    quem tem menos (empate: ordem alfabética do nome).
    """
    acumulado = {}
    for tarefa in tarefas:
        if tarefa.responsavel not in acumulado:
            acumulado[tarefa.responsavel] = {"total": 0, "em_aberto": 0, "atrasadas": 0}
        dados = acumulado[tarefa.responsavel]
        dados["total"] += 1
        if esta_em_aberto(tarefa):
            dados["em_aberto"] += 1
        if esta_atrasada(tarefa, data_referencia):
            dados["atrasadas"] += 1

    resumos = [
        ResumoResponsavel(nome, d["total"], d["em_aberto"], d["atrasadas"])
        for nome, d in acumulado.items()
    ]
    resumos.sort(key=lambda resumo: (-resumo.total, resumo.responsavel))
    return resumos


def listar_atrasadas(tarefas, data_referencia):
    """Lista as tarefas atrasadas como pares (tarefa, dias_de_atraso).

    Ordem: mais atrasada primeiro; em empate, menor id primeiro.
    """
    atrasadas = []
    for tarefa in tarefas:
        dias = dias_de_atraso(tarefa, data_referencia)
        if dias > 0:
            atrasadas.append((tarefa, dias))
    atrasadas.sort(key=lambda par: (-par[1], par[0].id))
    return atrasadas


def analisar(unicas, rejeitadas, duplicadas, data_referencia):
    """Reúne todos os indicadores num ResultadoAnalise.

    unicas: tarefas válidas sem duplicatas.
    rejeitadas: registros rejeitados (leitura + validação), em qualquer ordem.
    duplicadas: registros descartados por id repetido.
    """
    return ResultadoAnalise(
        data_referencia=data_referencia,
        total_lidas=len(unicas) + len(rejeitadas) + len(duplicadas),
        total_unicas=len(unicas),
        rejeitadas=sorted(rejeitadas, key=lambda registro: registro.numero_linha),
        duplicadas=duplicadas,
        por_status=contar_por_status(unicas),
        por_prioridade=contar_por_prioridade(unicas),
        por_responsavel=resumir_por_responsavel(unicas, data_referencia),
        atrasadas=listar_atrasadas(unicas, data_referencia),
    )