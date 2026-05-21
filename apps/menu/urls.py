from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("recipe/<int:pk>/", views.recipe_detail, name="recipe_detail"),
]
