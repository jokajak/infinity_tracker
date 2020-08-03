from django.urls import path

from . import views

urlpatterns = [
    path("<serial>", views.systems_overview),
    path("<serial>/profile", views.systems_profile),
    path("<serial>/dealer", views.systems_dealer),
    path("<path:path>", views.default_handler),
]
