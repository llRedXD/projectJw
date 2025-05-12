from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from designation.models import Parte, Pessoa, Reuniao


def index(request, error=None):
    reuniao = Reuniao.objects.all()
    return render(request, "index.html", {"reuniao": reuniao, "error": error})


def reuniao(request, reuniao_id):
    reuniao = Reuniao.objects.get(id=reuniao_id)
    partes = Parte.objects.filter(reuniao=reuniao)
    partes_tesouros = partes.filter(trecho="Tesouros da Palavra de Deus").order_by(
        "numero_parte"
    )
    partes_ministerio = partes.filter(trecho="Faça seu Melhor no Ministério").order_by(
        "numero_parte"
    )
    pessoas = Pessoa.objects.all()
    return render(
        request,
        "reuniao.html",
        {
            "reuniao": reuniao,
            "partes": partes,
            "pessoas": pessoas,
            "tesouros": partes_tesouros,
            "ministerio": partes_ministerio,
        },
    )


def update_parte(request, pk):
    if request.method == "POST":
        parte = get_object_or_404(Parte, pk=pk)
        reuniao = parte.reuniao
        # Atualiza campos básicos
        try:
            parte.numero_parte = request.POST.get("numero_parte", parte.numero_parte)
            if (
                Parte.objects.filter(reuniao=reuniao, numero_parte=parte.numero_parte)
                .exclude(pk=parte.pk)
                .exists()
            ):
                reorder_partes(reuniao, parte)

            parte.nome_parte = request.POST.get("nome_parte", parte.nome_parte)
            parte.duracao = (
                int(request.POST.get("duracao")) if request.POST.get("duracao") else 0
            )
            parte.pessoa_b = get_pessoa(request.POST.get("pessoa_b"))
            parte.ajudante_b = get_pessoa(request.POST.get("ajudante_b"))
            parte.pessoa = get_pessoa(request.POST.get("pessoa"))
            parte.ajudante = get_pessoa(request.POST.get("ajudante"))
            parte.ponto_parte = request.POST.get("ponto_parte", parte.ponto_parte)
            parte.save()
            return redirect("reuniao", reuniao.pk)
        except ValueError as e:
            return redirect("reuniao", reuniao.pk, {"error": str(e)})


def get_pessoa(nome):
    try:
        pessoa = Pessoa.objects.get(nome=nome)
    except Pessoa.DoesNotExist:
        return None
    return pessoa


def verificar_quantidade_parte(reuniao, trecho):
    if trecho == "Tesouros da Palavra de Deus":
        return Parte.objects.filter(reuniao=reuniao, trecho=trecho).count() < 3
    if trecho == "Faça seu Melhor no Ministério":
        return Parte.objects.filter(reuniao=reuniao, trecho=trecho).count() < 4
    if trecho == "Nossa Vida Cristã":
        return Parte.objects.filter(reuniao=reuniao, trecho=trecho).count() < 3


def verificar_numero_parte(reuniao, numero_parte, trecho):
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

    if (
        numero_parte == maximo
        and Parte.objects.filter(reuniao=reuniao, numero_parte=numero_parte).exists()
    ):
        return False

    return True


def reorder_partes(
    reuniao,
    parte,
):
    """
    Reordena as partes do trecho de forma que não existam lacunas ou sobreposições.
    Toda vez que um número de parte for alterado, as partes do mesmo trecho serão
    renumeradas sequencialmente, respeitando os limites estabelecidos.
    Exemplo: se o limite for de 4 a 7 e uma parte for movida para o número 4,
    as demais serão renumeradas a partir do 4, evitando conflitos (por exemplo,
    a peça que antes era 6 pode passar a ser 7 ou 8, se necessário, desde que
    não exceda o limite permitido).
    """
    trecho = parte.trecho
    numero_parte = parte.numero_parte

    limites = {
        "Tesouros da Palavra de Deus": (1, 3),
        "Faça seu Melhor no Ministério": (4, 7),
        "Nossa Vida Cristã": (7, 9),
    }
    if trecho not in limites:
        raise ValueError("Trecho inválido.")

    minimo, maximo = limites[trecho]
    partes = (
        Parte.objects.filter(reuniao=reuniao, trecho=trecho)
        .exclude(pk=parte.pk)
        .order_by("numero_parte")
    )
    total = partes.count()
    max_possible = maximo - minimo + 1

    if total > max_possible:
        raise ValueError("Número de partes excede o limite permitido.")

    # Reordena para que fiquem sequenciais a partir do limite mínimo
    novo_numero = minimo
    for parte in partes:
        if int(numero_parte) == parte.numero_parte:
            novo_numero += 1
        parte.numero_parte = novo_numero
        parte.save()
        novo_numero += 1


def create_parte(request, pk):
    if request.method == "POST":
        reuniao = get_object_or_404(Reuniao, pk=pk)
        numero_parte_nova = int(request.POST.get("numero_parte_nova"))
        trecho = request.POST.get("trecho")
        try:
            if not verificar_quantidade_parte(reuniao, trecho):
                raise ValueError(
                    "Já existe a quantidade máxima de partes para esse trecho."
                )
            # Verifica se já existe uma parte com o mesmo numero_parte
            parte = Parte(
                reuniao=reuniao,
                numero_parte=numero_parte_nova,
                trecho=trecho,
            )
            parte.full_clean()
            parte.save()

            # Reorganiza os números das partes, incrementando em 1 as partes com numero_parte >= numero_parte_nova
            if (
                Parte.objects.filter(reuniao=reuniao, numero_parte=parte.numero_parte)
                .exclude(pk=parte.pk)
                .exists()
            ):
                # Reorganiza os números das partes, incrementando em 1 as partes com numero_parte >= numero_parte_nova
                reorder_partes(reuniao, parte)

            return redirect("reuniao", reuniao.pk)
        except ValueError as e:
            return redirect("reuniao", pk)


def delete_parte(request, pk):
    if request.method == "POST":
        parte = get_object_or_404(Parte, pk=pk)
        reuniao = parte.reuniao
        parte.delete()
        return redirect("reuniao", reuniao.pk)
    return render(request, "delete_parte.html", {"parte": parte})
