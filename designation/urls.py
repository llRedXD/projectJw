from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("reuniao/<int:reuniao_id>/", views.reuniao, name="reuniao"),
]
