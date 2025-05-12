from django.shortcuts import get_object_or_404, redirect, render

from designation.models import Parte, Pessoa, Reuniao


def index(request):
    reuniao = Reuniao.objects.all()
    return render(request, "index.html", {"reuniao": reuniao})


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
        parte.numero_parte = request.POST.get(
            f"numero_parte_{parte.id}", parte.numero_parte
        )
        parte.nome_parte = request.POST.get(f"nome_parte_{parte.id}", parte.nome_parte)
        parte.duracao = (
            int(request.POST.get(f"duracao_{parte.id}"))
            if request.POST.get(f"duracao_{parte.id}")
            else 0
        )
        parte.pessoa_b = get_pessoa(request.POST.get(f"pessoa_b_{parte.id}"))
        parte.ajudante_b = get_pessoa(request.POST.get(f"ajudante_b_{parte.id}"))
        parte.pessoa = get_pessoa(request.POST.get(f"pessoa_{parte.id}"))
        parte.ajudante = get_pessoa(request.POST.get(f"ajudante_{parte.id}"))
        parte.ponto_parte = request.POST.get(
            f"ponto_parte_{parte.id}", parte.ponto_parte
        )
        parte.save()
        return redirect("reuniao", reuniao.pk)


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


def create_parte(request, pk):
    if request.method == "POST":
        reuniao = get_object_or_404(Reuniao, pk=pk)
        numero_parte_nova = int(request.POST.get("numero_parte_nova"))
        trecho = request.POST.get("trecho")
        if not verificar_quantidade_parte(reuniao, trecho):
            return redirect("reuniao", pk)
        # Verifica se já existe uma parte com o mesmo numero_parte
        if Parte.objects.filter(
            reuniao=reuniao, numero_parte=numero_parte_nova
        ).exists():
            # Reorganiza os números das partes, incrementando em 1 as partes com numero_parte >= numero_parte_nova
            partes_para_atualizar = Parte.objects.filter(
                reuniao=reuniao, numero_parte__gte=numero_parte_nova
            ).order_by("-numero_parte")
            for parte in partes_para_atualizar:
                parte.numero_parte += 1
                parte.save()
        parte = Parte(
            reuniao=reuniao,
            numero_parte=numero_parte_nova,
            trecho=trecho,
        )
        parte.full_clean()
        parte.save()

    return redirect("reuniao", pk)


def delete_parte(request, pk):
    if request.method == "POST":
        parte = get_object_or_404(Parte, pk=pk)
        reuniao = parte.reuniao
        parte.delete()
        return redirect("reuniao", reuniao.pk)
    return render(request, "delete_parte.html", {"parte": parte})
