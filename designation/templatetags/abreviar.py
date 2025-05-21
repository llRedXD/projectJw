from django import template

from designation.models import Pessoa

register = template.Library()


@register.filter
def abreviar(pessoa: Pessoa) -> str:
    """
    Se o nome tiver 2+ palavras retorna 'PrimeiroNome I.' senão devolve como está.
    """
    partes = pessoa.nome.split()
    if len(partes) >= 2:
        return f"{partes[0]} {partes[1][0]}."
    return pessoa.nome
