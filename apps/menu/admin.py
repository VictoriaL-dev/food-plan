from django.contrib import admin
from .models import Menu, Recipe, Ingredient


@admin.register(Menu)
class MenuTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'meal_type', 'menu_type', 'calories')
    list_filter = ('meal_type', 'menu_type')
    inlines = [IngredientInline]
