import datetime
from django.db import transaction

from apps.menu.models import Recipe
from .models import Order, DailyRation


class OrderRationService:
    """Сервис для управления и генерации рационов."""

    @staticmethod
    def generate_rations_for_order(order: Order, start_date: datetime.date = None):
        """Генерирует и фиксирует в БД рацион на весь срок подписки."""

        if start_date is None:
            start_date = datetime.date.today()

        total_days = order.duration * 30

        allowed_meals = []
        if order.has_breakfast:
            allowed_meals.append(Recipe.MealTypes.BREAKFAST)
        if order.has_lunch:
            allowed_meals.append(Recipe.MealTypes.LUNCH)
        if order.has_dinner:
            allowed_meals.append(Recipe.MealTypes.DINNER)
        if order.has_dessert:
            allowed_meals.append(Recipe.MealTypes.DESSERT)

        if not allowed_meals:
            return

        available_recipes = Recipe.objects.filter(
            menu_type=order.menu_type
        ).exclude(
            allergens__in=order.excluded_allergens.all()
        )

        rations_to_create = []

        with transaction.atomic():
            order.daily_rations.all().delete()

            for day_offset in range(total_days):
                current_date = start_date + datetime.timedelta(days=day_offset)

                ration_data = {
                    "order": order,
                    "date": current_date,
                    "total_calories": 0
                }

                for meal in allowed_meals:
                    recipe = available_recipes.filter(meal_type=meal).order_by('?').first()

                    if recipe:
                        field_name = meal.lower()
                        ration_data[field_name] = recipe
                        ration_data["total_calories"] += recipe.calories
                rations_to_create.append(DailyRation(**ration_data))

            DailyRation.objects.bulk_create(rations_to_create)
