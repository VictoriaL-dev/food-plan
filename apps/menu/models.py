from django.db import models
from django.utils.translation import gettext_lazy as _


class Allergen(models.Model):
    """Модель аллергенов."""
    
    name = models.CharField(_("Аллерген"), max_length=100, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = _("Аллерген")
        verbose_name_plural = _("Аллергены")

    def __str__(self):
        return self.name
    
    
class Menu(models.Model):
    """Модель типов меню."""
    
    name = models.CharField(_("Название меню"), max_length=50, unique=True)
    image = models.ImageField(_("Картинка меню"), upload_to="menu/menu_types/", blank=True)

    class Meta:
        verbose_name = _("Тип меню")
        verbose_name_plural = _("Типы меню")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    class MealTypes(models.TextChoices):
        BREAKFAST = "breakfast", _("Завтрак")
        LUNCH = "lunch", _("Обед")
        DINNER = "dinner", _("Ужин")
        DESSERT = "dessert", _("Десерт")

    title = models.CharField(_("Название"), max_length=200, unique=True)
    instructions = models.TextField(_("Рецепт приготовления"))
    calories = models.PositiveIntegerField(_("Калории"), default=0)
    meal_type = models.CharField(
        _("Тип приёма пищи"),
        max_length=20,
        choices=MealTypes.choices,
        default=MealTypes.BREAKFAST
    )
    menu_type = models.ForeignKey(
        Menu,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recipes",
        verbose_name=_("Тип меню")
    )
    allergens = models.ManyToManyField(
        Allergen, 
        blank=True, 
        related_name="recipes", 
        verbose_name=_("Аллергены в блюде")
    )
    image = models.ImageField(_("Картинка"), upload_to="menu/recipes/", blank=True)

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Модель ингредиентов блюда."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name=_("Рецепт")
    )
    name = models.CharField(_("Ингредиент"), max_length=200)
    amount = models.CharField(_("Количество"), max_length=50)

    class Meta:
        verbose_name = _("Ингредиент")
        verbose_name_plural = _("Ингредиенты")

    def __str__(self):
        return f"{self.name} — {self.amount}"
