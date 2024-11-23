from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("logout", views.logout_user, name="logout"),
    path("vacaciones", views.request_vacation, name="vacations"),
]
