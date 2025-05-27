from django.urls import path
from designation import views

urlpatterns = [
    # Rota sem parâmetros - usa valores default
    path("reunioes/", views.reunioes, name="reunioes"),
    # Rota com parâmetros
    path("reunioes/<int:mes>/<int:ano>/", views.reunioes, name="reunioes_param"),
    # ...existing code...
]
