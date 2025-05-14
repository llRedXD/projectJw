from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("reuniao/<int:reuniao_id>/", views.reuniao, name="reuniao"),
    path(
        "reuniao/<int:pk>/update_reuniao/",
        views.update_reuniao,
        name="update_reuniao",
    ),
    path(
        "reuniao/<int:pk>/update_parte/",
        views.update_parte,
        name="update_parte",
    ),
    path(
        "reuniao/<int:pk>/create_parte/",
        views.create_parte,
        name="create_parte",
    ),
    path(
        "reuniao/<int:pk>/delete_parte/",
        views.delete_parte,
        name="delete_parte",
    ),
]
