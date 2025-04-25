from django import forms
from django.contrib import admin
from .models import Pessoa, Reuniao, Parte
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
        "pessoa",
        "ajudante",
        "pessoa_b",
        "ajudante_b",
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
                    "oracao_inicial",
                    "cantico_meio",
                    "cantico_final",
                    "oracao_final",
                    "presidente",
                    "conselheiro_sala_b",
                )
            },
        ),
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
    )
    search_fields = ("reuniao__data", "nome_parte")
    list_filter = ("reuniao",)
