from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.index, name="index"),
    path("order", views.make_order, name="order"),
    path('reviews/', views.reviews_view, name='reviews'),

]
