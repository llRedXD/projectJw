from django.shortcuts import render

from designation.models import Parte, Reuniao


def index(request):
    reuniao = Reuniao.objects.all()
    return render(request, "index.html", {"reuniao": reuniao})


def reuniao(request, reuniao_id):
    reuniao = Reuniao.objects.get(id=reuniao_id)
    partes = Parte.objects.filter(reuniao=reuniao)
    return render(request, "reuniao.html", {"reuniao": reuniao, "partes": partes})
