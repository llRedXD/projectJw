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
    cantico_inicial = models.CharField(max_length=100)
    cantico_meio = models.CharField(max_length=100)
    cantico_final = models.CharField(max_length=100)

    def __str__(self):
        return f"Reunião em {self.data} - {self.texto}"


class Parte(models.Model):
    reuniao = models.ForeignKey(Reuniao, on_delete=models.CASCADE)
    numero_parte = models.IntegerField()
    ordem_parte = models.IntegerField()
    nome_parte = models.CharField(max_length=100)
    ponto_parte = models.CharField(max_length=100, blank=True, null=True)
    duracao = models.IntegerField()
    sala_b = models.BooleanField(default=False)

    def __str__(self):
        return f"Parte {self.numero_parte} - {self.nome_parte} ({self.reuniao.data})"


class Designacao(models.Model):
    parte = models.ForeignKey(Parte, on_delete=models.CASCADE)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.pessoa.nome} - {self.parte.nome_parte} ({self.parte.reuniao.data})"
        )
