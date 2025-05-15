from django.db import models


class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    publicador = models.BooleanField(default=False)
    indicador = models.BooleanField(default=False)
    leitor_livro = models.BooleanField(default=False)
    leitor_sentinela = models.BooleanField(default=False)
    microfone = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Reuniao(models.Model):
    data = models.DateField()
    texto = models.CharField(max_length=100)
    cantico_inicial = models.CharField(max_length=100, null=True, blank=True)
    cantico_meio = models.CharField(max_length=100, null=True, blank=True)
    cantico_final = models.CharField(max_length=100, null=True, blank=True)
    oracao_inicial = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="oracao_inicial",
        null=True,
        blank=True,
    )
    oracao_final = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="oracao_final",
        null=True,
        blank=True,
    )
    presidente = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="presidente",
        null=True,
        blank=True,
    )
    conselheiro_sala_b = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="conselheiro_sala_b",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.data.strftime('%d de %B')} | {self.texto}"


class Trecho(models.Choices):
    TESOUROS = "Tesouros da Palavra de Deus"
    MINISTERIO = "Faça seu Melhor no Ministério"
    VIDA_CRISTA = "Nossa Vida Cristã"


class Parte(models.Model):
    reuniao = models.ForeignKey(Reuniao, on_delete=models.CASCADE)
    numero_parte = models.PositiveIntegerField()
    trecho = models.CharField(
        max_length=50,
        choices=Trecho.choices,  # type: ignore
    )
    nome_parte = models.CharField(max_length=100, blank=True, null=True)
    ponto_parte = models.CharField(max_length=100, blank=True, null=True)
    duracao = models.PositiveIntegerField(default=0)
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="parte",
        blank=True,
        null=True,
    )
    ajudante = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="ajudante",
        blank=True,
        null=True,
    )
    pessoa_b = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="pessoa_b",
        blank=True,
        null=True,
    )
    ajudante_b = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="ajudante_b",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Parte {self.numero_parte} - {self.nome_parte} ({self.reuniao.data})"

    # class Meta:
    # unique_together = (
    #     "reuniao",
    #     "numero_parte",
    # )
