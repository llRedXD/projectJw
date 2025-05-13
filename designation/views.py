from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from designation.models import Parte, Pessoa, Reuniao


# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Views principais                                                         │
# └───────────────────────────────────────────────────────────────────────────┘
def index(request, error=None):
    """
    Exibe a lista de todas as reuniões.
    Parâmetros:
      - request: objeto HttpRequest
      - error: mensagem de erro opcional
    """
    reunioes = Reuniao.objects.all()
    return render(request, "index.html", {"reuniao": reunioes, "error": error})


def reuniao(request, reuniao_id, error=None):
    """
    Exibe os detalhes de uma reunião específica, incluindo suas partes e pessoas.
    Parâmetros:
      - request: objeto HttpRequest
      - reuniao_id: ID da reunião
      - error: mensagem de erro opcional
    """
    reuniao = get_object_or_404(Reuniao, id=reuniao_id)
    partes = Parte.objects.filter(reuniao=reuniao)
    tesouros = partes.filter(trecho="Tesouros da Palavra de Deus").order_by(
        "numero_parte"
    )
    ministerio = partes.filter(trecho="Faça seu Melhor no Ministério").order_by(
        "numero_parte"
    )
    vida_crista = partes.filter(trecho="Nossa Vida Cristã").order_by("numero_parte")
    pessoas = Pessoa.objects.all()
    return render(
        request,
        "reuniao.html",
        {
            "reuniao": reuniao,
            "partes": partes,
            "pessoas": pessoas,
            "tesouros": tesouros,
            "ministerio": ministerio,
            "vida_crista": vida_crista,
            "error": error,
        },
    )


# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Operações CRUD sobre Parte                                               │
# └───────────────────────────────────────────────────────────────────────────┘
def create_parte(request, pk):
    """
    Cria uma nova parte em uma reunião.
    - Verifica limites por trecho.
    - Ajusta ordenação caso haja conflito de número.
    """
    if request.method != "POST":
        return redirect("reuniao", pk)
    reuniao = get_object_or_404(Reuniao, pk=pk)
    numero = int(request.POST.get("numero_parte_nova"))
    trecho = request.POST.get("trecho")
    try:
        if not verificar_quantidade_parte(reuniao, trecho):
            raise ValueError("Quantidade máxima de partes atingida para este trecho.")
        parte = Parte(reuniao=reuniao, numero_parte=numero, trecho=trecho)
        parte.full_clean()
        parte.save()
        # Se houver outra parte com este número, reordena
        if (
            Parte.objects.filter(reuniao=reuniao, numero_parte=numero)
            .exclude(pk=parte.pk)
            .exists()
        ):
            reorder_partes(reuniao, parte)
        return redirect("reuniao", reuniao.pk)
    except ValueError:
        return redirect("reuniao", pk)


def update_parte(request, pk):
    """
    Atualiza os campos de uma parte existente.
    - Renumera automaticamente se houver conflito de número.
    - Trata erros de conversão e valores inválidos.
    """
    if request.method != "POST":
        return redirect("reuniao", pk)
    parte = get_object_or_404(Parte, pk=pk)
    reuniao = parte.reuniao
    try:
        # Atualiza campos básicos
        parte.numero_parte = int(request.POST.get("numero_parte", parte.numero_parte))
        if (
            Parte.objects.filter(reuniao=reuniao, numero_parte=parte.numero_parte)
            .exclude(pk=pk)
            .exists()
        ):
            reorder_partes(reuniao, parte)
        parte.nome_parte = request.POST.get("nome_parte", parte.nome_parte)
        parte.duracao = int(request.POST.get("duracao", 0))
        parte.pessoa_b = get_pessoa(request.POST.get("pessoa_b"))
        parte.ajudante_b = get_pessoa(request.POST.get("ajudante_b"))
        parte.pessoa = get_pessoa(request.POST.get("pessoa"))
        parte.ajudante = get_pessoa(request.POST.get("ajudante"))
        parte.ponto_parte = request.POST.get("ponto_parte", parte.ponto_parte)
        parte.save()
        return redirect("reuniao", reuniao.pk)
    except (ValueError, TypeError) as e:
        return redirect("reuniao", reuniao.pk, {"error": str(e)})


def delete_parte(request, pk):
    """
    Exclui uma parte de uma reunião.
    """
    parte = get_object_or_404(Parte, pk=pk)
    if request.method == "POST":
        reuniao_pk = parte.reuniao.pk
        parte.delete()
        return redirect("reuniao", reuniao_pk)
    return render(request, "delete_parte.html", {"parte": parte})


# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Funções auxiliares                                                       │
# └───────────────────────────────────────────────────────────────────────────┘
def get_pessoa(nome):
    """
    Retorna a instância de Pessoa pelo nome ou None se não existir.
    """
    try:
        return Pessoa.objects.get(nome=nome)
    except Pessoa.DoesNotExist:
        return None


def verificar_quantidade_parte(reuniao, trecho):
    """
    Verifica se ainda há vagas para novas partes no trecho especificado.
    Limites:
      - Tesouros da Palavra de Deus: máximo 3
      - Faça seu Melhor no Ministério: máximo 4
      - Nossa Vida Cristã: máximo 3
    """
    limites = {
        "Tesouros da Palavra de Deus": 3,
        "Faça seu Melhor no Ministério": 4,
        "Nossa Vida Cristã": 3,
    }
    return Parte.objects.filter(reuniao=reuniao, trecho=trecho).count() < limites.get(
        trecho, 0
    )


def verificar_numero_parte(reuniao, numero_parte, trecho):
    """
    Valida se o número da parte está dentro dos limites do trecho e
    se não ocasionará conflito no final da sequência.
    """
    limites = {
        "Tesouros da Palavra de Deus": (1, 3),
        "Faça seu Melhor no Ministério": (4, 7),
        "Nossa Vida Cristã": (7, 9),
    }
    if trecho not in limites:
        raise ValueError("Trecho inválido.")
    minimo, maximo = limites[trecho]
    if not (minimo <= numero_parte <= maximo):
        return False
    # Última posição não pode estar duplicada
    if (
        numero_parte == maximo
        and Parte.objects.filter(reuniao=reuniao, numero_parte=numero_parte).exists()
    ):
        return False
    return True


def reorder_partes(reuniao, parte):
    """
    Renumera todas as partes de um trecho para evitar lacunas ou sobreposições.
    Exemplo: ao inserir/mover uma parte para o número 4 (num trecho com limite 4–7),
    as demais são renumeradas sequencialmente respeitando o máximo permitido.
    """
    trecho = parte.trecho
    limites = {
        "Tesouros da Palavra de Deus": (1, 3),
        "Faça seu Melhor no Ministério": (4, 7),
        "Nossa Vida Cristã": (7, 9),
    }
    if trecho not in limites:
        raise ValueError("Trecho inválido.")
    minimo, maximo = limites[trecho]

    partes = (
        Parte.objects.filter(reuniao=reuniao, numero_parte__gte=minimo)
        .exclude(pk=parte.pk)
        .order_by("numero_parte")
    )
    total = partes.count()
    max_slots = maximo - minimo + 1
    if total > max_slots:
        raise ValueError("Número de partes excede o limite permitido.")

    novo_num = minimo
    with transaction.atomic():
        for p in partes:
            # Se coincidir com a posição do novo/movido, avança um slot
            if novo_num == parte.numero_parte:
                novo_num += 1
            p.numero_parte = novo_num
            p.save()
            novo_num += 1
