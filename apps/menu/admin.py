from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Allergen, Menu, Recipe, Ingredient


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_recipes_count")
    search_fields = ("name",)

    @admin.display(description="Кол-во блюд с этим аллергеном")
    def get_recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("get_image_preview", "name", "get_recipes_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("id",)

    @admin.display(description="Фото")
    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />')
        return mark_safe('<span style="color: #999;">Нет фото</span>')

    @admin.display(description="Всего рецептов в меню")
    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    classes = ("collapse",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "get_image_preview", "title", "meal_type", "menu_type", "get_ingredients_count")
    list_display_links = ("title",)
    list_filter = ("meal_type", "menu_type", "allergens")
    search_fields = ("title", "ingredients__name")
    filter_horizontal = ("allergens",)
    ordering = ("-id",)

    inlines = [IngredientInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("menu_type").prefetch_related("ingredients")

    @admin.display(description="Фото")
    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 4px;" />')
        return mark_safe('<span style="color: #999;">Нет фото</span>')

    @admin.display(description="Ингредиентов")
    def get_ingredients_count(self, obj):
        return obj.ingredients.count()
