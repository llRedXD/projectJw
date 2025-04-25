from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("reuniao/<int:reuniao_id>/", views.reuniao, name="reuniao"),
    path(
        "reuniao/<int:pk>/update_partes/",
        views.reuniao_update_partes,
        name="reuniao_update_partes",
    ),
]
