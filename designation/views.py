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


def create_parte(request, pk):
    if request.method == "POST":
        reuniao = get_object_or_404(Reuniao, pk=pk)
        pessoa = get_pessoa(request.POST.get("pessoa"))
        pessoa_b = get_pessoa(request.POST.get("pessoa_b"))

        parte = Parte(
            reuniao=reuniao,
            numero_parte=request.POST.get("numero_parte"),
            trecho=request.POST.get("trecho"),
            nome_parte=request.POST.get("nome_parte"),
            ponto_parte=request.POST.get("ponto_parte"),
            duracao=int(request.POST.get("duracao"))
            if request.POST.get("duracao")
            else 0,
            pessoa=pessoa,
            pessoa_b=pessoa_b,
        )
        parte.save()
        return redirect("reuniao", reuniao.pk)


def delete_parte(request, pk):
    if request.method == "POST":
        parte = get_object_or_404(Parte, pk=pk)
        reuniao = parte.reuniao
        parte.delete()
        return redirect("reuniao", reuniao.pk)
    return render(request, "delete_parte.html", {"parte": parte})
