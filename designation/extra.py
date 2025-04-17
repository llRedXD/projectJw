from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe


class ComboBoxWidget(TextInput):
    def __init__(self, suggestions=None, attrs=None):
        self.suggestions = suggestions or []
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        # Define um ID para o input, usado também para o datalist
        input_id = attrs.get("id", f"id_{name}")
        datalist_id = f"{input_id}_list"

        # Insere o atributo list para associar o input ao datalist
        attrs["list"] = datalist_id
        input_html = super().render(name, value, attrs, renderer)

        # Cria as opções do datalist a partir das sugestões
        options = "".join(
            [f"<option value='{suggestion}'>" for suggestion in self.suggestions]
        )
        datalist_html = f"<datalist id='{datalist_id}'>{options}</datalist>"

        return mark_safe(input_html + datalist_html)
