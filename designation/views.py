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
    pessoas = Pessoa.objects.all()
    return render(
        request,
        "reuniao.html",
        {
            "reuniao": reuniao,
            "partes": partes,
            "tesouros": partes_tesouros,
            "pessoas": pessoas,
        },
    )


def reuniao_update_partes(request, pk):
    reuniao = get_object_or_404(Reuniao, pk=pk)
    if request.method == "POST":
        confirm_pk = request.POST.get("confirmar_pk")
        if confirm_pk:
            parte = get_object_or_404(Parte, pk=confirm_pk, reuniao=reuniao)
            # Atualiza campos básicos
            parte.numero_parte = request.POST.get(
                f"partes-{confirm_pk}-numero_parte", parte.numero_parte
            )
            parte.nome_parte = request.POST.get(
                f"partes-{confirm_pk}-nome_parte", parte.nome_parte
            )
            # Converter string para int, se existir
            dur = request.POST.get(f"partes-{confirm_pk}-duracao")
            if dur:
                parte.duracao = int(dur)
            pessoa_b = request.POST.get(f"partes-{confirm_pk}-pessoa_b")
            if pessoa_b == "":
                parte.pessoa_b = None
            parte.pessoa_b = Pessoa.objects.filter(pk=pessoa_b).first()
            parte.ponto_parte = request.POST.get(
                f"partes-{confirm_pk}-ponto_parte", parte.ponto_parte
            )
            pessoa = request.POST.get(f"partes-{confirm_pk}-pessoa")
            pessoa = Pessoa.objects.filter(pk=pessoa).first()
            parte.pessoa = pessoa
            parte.save()
        return redirect("reuniao", reuniao.pk)
