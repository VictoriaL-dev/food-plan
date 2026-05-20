from django.shortcuts import get_object_or_404, render
from .models import Recipe


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'card3.html', {'recipe': recipe})
