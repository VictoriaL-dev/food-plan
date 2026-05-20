from django.db import models


class Menu(models.Model):
    MENU_CHOICES = [
        ('classic', 'Классическое'),
        ('low_carb', 'Низкоуглеводное'),
        ('vegetarian', 'Вегетарианское'),
    ]
    name = models.CharField(
        max_length=20,
        choices=MENU_CHOICES,
        unique=True,
        verbose_name='Тип меню'
    )

    class Meta:
        verbose_name = 'Тип меню'
        verbose_name_plural = 'Типы меню'

    def __str__(self):
        return self.get_name_display()


class Recipe(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('dessert', 'Десерт'),
    ]

    title = models.CharField('Название', max_length=200)
    instructions = models.TextField('Рецепт приготовления')
    calories = models.PositiveIntegerField('Калории', default=0)
    meal_type = models.CharField('Тип приёма пищи', max_length=20, choices=MEAL_TYPES)
    menu_type = models.ForeignKey(
        Menu,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Тип меню'
    )
    image = models.ImageField('Картинка', upload_to='recipes/', blank=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    name = models.CharField('Ингредиент', max_length=200)
    amount = models.CharField('Количество (г)', max_length=100)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} — {self.amount}'
