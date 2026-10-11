"""Validação e conversão dos registros lidos do CSV."""

from datetime import datetime

from taskflow.modelos import RegistroRejeitado, Tarefa

STATUS_VALIDOS = ("aberta", "em_andamento", "concluida", "cancelada")
PRIORIDADES_VALIDAS = ("baixa", "media", "alta")
FORMATO_DATA = "%Y-%m-%d"


def converter_data(texto):
    """Converte 'AAAA-MM-DD' em date. Levanta ValueError se for inválida."""
    return datetime.strptime(texto, FORMATO_DATA).date()


def _ler_id(campos, erros):
    texto = campos["id"]
    if not texto:
        erros.append("id vazio")
        return None
    try:
        valor = int(texto)
    except ValueError:
        erros.append(f"id inválido: {texto!r}")
        return None
    if valor <= 0:
        erros.append(f"id deve ser positivo: {texto!r}")
        return None
    return valor


def _ler_texto(campos, nome, erros):
    texto = campos[nome]
    if not texto:
        erros.append(f"{nome} vazio")
        return None
    return texto


def _ler_opcao(campos, nome, validos, erros):
    texto = campos[nome].lower()
    if not texto:
        erros.append(f"{nome} vazio")
        return None
    if texto not in validos:
        erros.append(f"{nome} inválido: {campos[nome]!r}")
        return None
    return texto


def _ler_data(campos, nome, erros):
    texto = campos[nome]
    if not texto:
        erros.append(f"{nome} vazio")
        return None
    try:
        return converter_data(texto)
    except ValueError:
        erros.append(f"{nome} inválido: {texto!r}")
        return None


def validar_linha(numero_linha, linha):
    """Valida uma linha (dicionário de textos).

    Devolve (tarefa, erros). Se houver qualquer erro, tarefa é None
    e erros lista todos os problemas encontrados.
    """
    campos = {nome: valor.strip() for nome, valor in linha.items()}
    erros = []

    id_tarefa = _ler_id(campos, erros)
    titulo = _ler_texto(campos, "titulo", erros)
    responsavel = _ler_texto(campos, "responsavel", erros)
    status = _ler_opcao(campos, "status", STATUS_VALIDOS, erros)
    prioridade = _ler_opcao(campos, "prioridade", PRIORIDADES_VALIDAS, erros)
    data_criacao = _ler_data(campos, "data_criacao", erros)
    prazo = _ler_data(campos, "prazo", erros)

    data_conclusao = None
    if campos["data_conclusao"]:
        data_conclusao = _ler_data(campos, "data_conclusao", erros)
    elif status == "concluida":
        erros.append("data_conclusao obrigatória para tarefa concluída")

    if data_criacao is not None and prazo is not None and prazo < data_criacao:
        erros.append("prazo anterior à data_criacao")

    if erros:
        return None, erros

    tarefa = Tarefa(
        numero_linha=numero_linha,
        id=id_tarefa,
        titulo=titulo,
        responsavel=responsavel,
        status=status,
        prioridade=prioridade,
        data_criacao=data_criacao,
        prazo=prazo,
        data_conclusao=data_conclusao,
    )
    return tarefa, []


def validar_linhas(linhas):
    """Valida todas as linhas. Devolve (tarefas, rejeitados)."""
    tarefas = []
    rejeitados = []
    for numero_linha, linha in linhas:
        tarefa, erros = validar_linha(numero_linha, linha)
        if tarefa is None:
            rejeitados.append(RegistroRejeitado(numero_linha, erros))
        else:
            tarefas.append(tarefa)
    return tarefas, rejeitados


def separar_duplicadas(tarefas):
    """Separa tarefas com id repetido.

    Recebe a lista de Tarefa válidas, na ordem do arquivo.
    Mantém a primeira ocorrência de cada id e descarta as seguintes.
    Devolve (unicas, duplicadas): as duplicadas são RegistroRejeitado
    que apontam para a linha da primeira ocorrência.
    """
    primeira_linha_por_id = {}
    unicas = []
    duplicadas = []

    for tarefa in tarefas:
        if tarefa.id in primeira_linha_por_id:
            linha_original = primeira_linha_por_id[tarefa.id]
            motivo = (
                f"id {tarefa.id} duplicado; "
                f"primeira ocorrência na linha {linha_original}"
            )
            duplicadas.append(RegistroRejeitado(tarefa.numero_linha, [motivo]))
        else:
            primeira_linha_por_id[tarefa.id] = tarefa.numero_linha
            unicas.append(tarefa)

    return unicas, duplicadas