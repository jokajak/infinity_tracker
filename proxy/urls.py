from django.urls import path

from . import views

urlpatterns = [
    path("<serial>", views.systems_overview),
    path("<serial>/profile", views.systems_profile),
    path("<serial>/dealer", views.systems_dealer),
    path("<serial>/status", views.systems_status),
    path("<serial>/notifications", views.systems_notifications),
    path("<serial>/idu_config", views.systems_idu_config),
    path("<serial>/odu_config", views.systems_odu_config),
    path("<serial>/equipment_events", views.systems_equipment_events),
    path("<path:path>", views.default_handler),
]
