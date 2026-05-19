from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.index, name="index"),
    path("card1", views.card1, name="card1"),
    path("card2", views.card2, name="card2"),
    path("card3", views.card3, name="card3"),
    path("order", views.make_order, name="order"),
    path("profile", views.show_profile, name="profile"),
    path("login", views.login, name="login"),
    path("registration", views.register, name="register"),
]
