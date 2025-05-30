from django import forms
from django.contrib import admin
from .models import Pessoa, Reuniao, Parte, Designacao
from .extra import ComboBoxWidget


class ParteForm(forms.ModelForm):
    class Meta:
        model = Parte
        fields = "__all__"
        widgets = {
            "nome_parte": ComboBoxWidget(
                suggestions=[
                    "Joias espirituais",
                    "Leitura da Biblia",
                    "Iniciando conversas",
                    "Cultivando o interesse",
                    "Explicando suas crenças",
                    "Necessidades Locais",
                    "Estudo Biblíco",
                ]
            ),
        }


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "publicador",
        "indicador",
        "leitor_livro",
        "leitor_sentinela",
        "microfone",
    )
    search_fields = ("nome",)
    list_filter = (
        "publicador",
        "indicador",
        "leitor_livro",
        "leitor_sentinela",
        "microfone",
    )


class ParteInline(admin.TabularInline):
    model = Parte
    extra = 0
    fields = (
        "numero_parte",
        "trecho",
        "nome_parte",
        "ponto_parte",
        "duracao",
        "sala_b",
    )
    form = ParteForm
    show_change_link = True


@admin.register(Reuniao)
class ReuniaoAdmin(admin.ModelAdmin):
    list_display = ("data", "texto", "cantico_inicial", "cantico_meio", "cantico_final")
    search_fields = ("data", "texto")
    list_filter = ("data",)
    fieldsets = (
        (
            "Informações iniciais",
            {
                "fields": (
                    "data",
                    "texto",
                    "cantico_inicial",
                    "presidente",
                    "conselheiro_sala_b",
                )
            },
        ),
        # ("Tesouros da Palavra de Deus", {"fields": ("cantico_meio", "oracao_inicial")}),
    )
    inlines = [
        ParteInline,
    ]


@admin.register(Parte)
class ParteAdmin(admin.ModelAdmin):
    form = ParteForm
    add_form = ParteForm
    list_display = (
        "reuniao",
        "numero_parte",
        "trecho",
        "nome_parte",
        "ponto_parte",
        "duracao",
        "sala_b",
    )
    search_fields = ("reuniao__data", "nome_parte")
    list_filter = ("reuniao", "sala_b")


@admin.register(Designacao)
class DesignacaoAdmin(admin.ModelAdmin):
    list_display = ("parte", "pessoa")
    search_fields = ("parte__nome_parte", "pessoa__nome")
    list_filter = ("parte", "pessoa")
