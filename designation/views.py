from datetime import date
from django.http import FileResponse, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.contrib import messages

from itertools import zip_longest

from docx import Document

from designation.models import Parte, Pessoa, Reuniao
from designation.services.generate_file import (
    end_tab5,
    format_table,
    get_tab1,
    get_tab2,
    get_tab3,
    get_tab4,
    get_tab5,
    get_tables,
    init_tab3,
    init_tab4,
    init_tab5,
)


# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Views principais                                                         │
# └───────────────────────────────────────────────────────────────────────────┘
def reunioes(request, mes: int | None = None, ano: int | None = None):
    """
    Exibe a lista de todas as reuniões.
    Parâmetros:
      - request: objeto HttpRequest
      - error: mensagem de erro opcional
    """
    mes = mes or date.today().month
    ano = ano or date.today().year
    reunioes = Reuniao.objects.filter(data__year=ano, data__month=mes).order_by("data")
    today = date.today()
    return render(request, "list_reunioes.html", {"reuniao": reunioes, "today": today})


def reuniao(request, reuniao_id):
    """
    Exibe os detalhes de uma reunião específica, incluindo suas partes e pessoas.
    Parâmetros:
      - request: objeto HttpRequest
      - reuniao_id: ID da reunião
      - error: mensagem de erro opcional
    """
    try:
        reuniao = get_object_or_404(Reuniao, id=reuniao_id)
        reuniao_anterior = (
            Reuniao.objects.filter(data__lt=reuniao.data).order_by("-data").first()
        )
        tesouros_anterior = Parte.objects.filter(
            reuniao=reuniao_anterior, trecho="Tesouros da Palavra de Deus"
        ).order_by("numero_parte")
        ministerio_anterior = Parte.objects.filter(
            reuniao=reuniao_anterior,
            trecho="Faça seu Melhor no Ministério",
        ).order_by("numero_parte")
        vida_crista_anterior = Parte.objects.filter(
            reuniao=reuniao_anterior, trecho="Nossa Vida Cristã"
        ).order_by("numero_parte")

        reuniao_posterior = (
            Reuniao.objects.filter(data__gt=reuniao.data).order_by("data").first()
        )
        tesouros_posterior = Parte.objects.filter(
            reuniao=reuniao_posterior, trecho="Tesouros da Palavra de Deus"
        ).order_by("numero_parte")
        ministerio_posterior = Parte.objects.filter(
            reuniao=reuniao_posterior,
            trecho="Faça seu Melhor no Ministério",
        ).order_by("numero_parte")
        vida_crista_posterior = Parte.objects.filter(
            reuniao=reuniao_posterior, trecho="Nossa Vida Cristã"
        ).order_by("numero_parte")

        partes = Parte.objects.filter(reuniao=reuniao)
        tesouros_atual = partes.filter(trecho="Tesouros da Palavra de Deus").order_by(
            "numero_parte"
        )
        ministerio_atual = partes.filter(
            trecho="Faça seu Melhor no Ministério"
        ).order_by("numero_parte")
        vida_crista_atual = partes.filter(trecho="Nossa Vida Cristã").order_by(
            "numero_parte"
        )
        pessoas = Pessoa.objects.all()

        # Zipar os querysets para facilitar o acesso
        tesouros = list(
            zip_longest(
                tesouros_atual,
                tesouros_anterior or [],
                tesouros_posterior or [],
                fillvalue=None,
            )
        )
        ministerio = list(
            zip_longest(
                ministerio_atual,
                ministerio_anterior or [],
                ministerio_posterior or [],
                fillvalue=None,
            )
        )
        vida_crista = list(
            zip_longest(
                vida_crista_atual,
                vida_crista_anterior or [],
                vida_crista_posterior or [],
                fillvalue=None,
            )
        )

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
                "reuniao_anterior": reuniao_anterior if reuniao_anterior else None,
                "reuniao_posterior": reuniao_posterior if reuniao_posterior else None,
            },
        )
    except Exception as e:
        messages.error(request, "Erro ao carregar reunião: " + str(e))
        return redirect("reuniao")


#   ┌─────────────────────────────────────────────────────────────────────────┐
#  | Operações CRUD sobre Reunião                                            │
# └─────────────────────────────────────────────────────────────────────────┘
def create_reuniao(request: HttpRequest):
    """
    Cria uma nova reunião.
    - Verifica se o ID da reunião é válido.
    - Cria uma nova reunião com os dados do formulário.
    """
    if request.method != "POST":
        return redirect("reuniao")
    try:
        reuniao = Reuniao(
            texto=request.POST.get("texto").upper(),  # type: ignore
            data=request.POST.get("data"),
        )
        if Reuniao.objects.filter(data=reuniao.data).exists():
            messages.error(request, "Já existe uma reunião nesta data.")
            raise ValueError("Já existe uma reunião nesta data.")
        reuniao.full_clean()
        reuniao.save()
        partes_to_create_reuniao(reuniao.pk)
        return redirect("reuniao", reuniao.pk)
    except Exception as e:
        messages.error(request, "Erro ao criar reunião: " + str(e))
        return redirect("reuniao")


def partes_to_create_reuniao(pk):
    """
    Criar as partes Basicas para uma nova reunião.

    Args:
        request (_type_): request
        pk (_type_): Primary Key da reunião
    """
    partes_tesouros = {1: "", 2: "Joias espirituais", 3: "Leitura da Bíblia"}
    partes_ministerio = {
        4: "Iniciando conversas",
        5: "Cultivando o interesse",
        6: "Cultivando o interesse",
    }
    partes_vida_crista = {7: "", 8: "Estudo da Biblico"}
    partes = partes_tesouros | partes_ministerio | partes_vida_crista
    for parte in partes:
        if parte in partes_tesouros:
            trecho = "Tesouros da Palavra de Deus"
        elif parte in partes_ministerio:
            trecho = "Faça seu Melhor no Ministério"
        else:
            trecho = "Nossa Vida Cristã"

        parte = Parte(
            reuniao=Reuniao.objects.get(pk=pk),
            numero_parte=parte,
            nome_parte=partes[parte],
            trecho=trecho,
        )
        parte.full_clean()
        parte.save()


def update_reuniao(request, pk):
    """
    Atualiza os campos de uma reunião existente.
    - Verifica se o ID da reunião é válido.
    - Atualiza os campos com base nos dados do formulário.
    """
    if request.method != "POST":
        return redirect("reuniao", pk)
    try:
        reuniao = get_object_or_404(Reuniao, pk=pk)
        reuniao.texto = request.POST.get("texto", reuniao.texto)
        reuniao.data = request.POST.get("data")
        reuniao.presidente = get_pessoa(request.POST.get("presidente"))
        reuniao.conselheiro_sala_b = get_pessoa(request.POST.get("conselheiro_sala_b"))
        reuniao.save()
        return redirect("reuniao", pk)
    except Exception as e:
        messages.error(request, "Erro ao atualizar reunião: " + str(e))
        return redirect("reuniao", pk)


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
        messages.error(request, "Número de parte inválido ou já existente.")
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
        verificar_numero_parte(reuniao, parte.numero_parte, parte.trecho)
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
        messages.error(request, "Erro ao atualizar parte: " + str(e))
        return redirect("reuniao", reuniao.pk)


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
# │ Adicionar Dados                                                          │
# └─────────────────────────────────────────────────────────────────────────┘
def gerar_arquivo(request, mes: int, ano: int):
    """
    Gera um arquivo com as reuniões do mês e ano especificados.
    - Verifica se o mês e ano são válidos.
    - Retorna um arquivo para download.
    """
    try:
        reunioes = Reuniao.objects.filter(data__year=ano, data__month=mes)
        if not reunioes.exists():
            messages.error(request, "Nenhuma reunião encontrada para este mês.")
            return redirect("list_reuniao")
        doc = Document("django_files/base_file.docx")
        # print(f"Gerando arquivo para {mes:02d}/{ano}...")
        count = 0
        for reuniao in reunioes.order_by("data"):
            doc_tab1, doc_tab2, doc_tab3, doc_tab4, doc_tab5 = get_tables(doc, count)
            tab1, tab2, tab3, tab4, tab5 = [], [], [], [], []
            get_tab1(reuniao, tab1)
            get_tab2(reuniao, tab2)
            init_tab3(tab3)
            init_tab4(tab4)
            init_tab5(reuniao, tab5)
            partes = Parte.objects.filter(reuniao=reuniao).order_by("numero_parte")
            for parte in partes:
                get_tab3(parte, tab3)
                get_tab4(parte, tab4)
                get_tab5(parte, tab5)
            end_tab5(reuniao, tab5)
            format_table(doc_tab1, tab1, [0, 2, 5])
            format_table(doc_tab2, tab2, [0, 1, 2, 3])
            format_table(doc_tab3, tab3)
            format_table(doc_tab4, tab4)
            format_table(doc_tab5, tab5)
            doc.save("django_files/new_file.docx")
            count += 5
        return JsonResponse(
            {"status": "success", "message": "Arquivo gerado com sucesso!"}
        )

        # return FileResponse(
        #     open("django_files/base_file.docx", "rb"),
        #     as_attachment=True,
        #     filename=f"reunioes_{mes:02d}_{ano}.txt",
        # )
        # return redirect("list_reuniao")  # Redireciona após gerar o arquivo
    except Exception as e:
        messages.error(request, "Erro ao gerar arquivo: " + str(e))
        return redirect("list_reuniao")


# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Funções auxiliares                                                       │
# └───────────────────────────────────────────────────────────────────────────┘
def get_pessoa(nome):
    """
    Retorna a instância de Pessoa pelo nome ou None se não existir.
    """
    try:
        if nome in ["", "None", None]:
            return None
        return Pessoa.objects.get(nome=nome)
    except Pessoa.DoesNotExist:
        raise ValueError(f"Pessoa '{nome}' não encontrada.")


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
        raise ValueError(
            f"Número de parte {numero_parte} fora dos limites para o trecho {trecho}."
        )
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
