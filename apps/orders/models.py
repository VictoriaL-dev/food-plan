from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class PromoCode(models.Model):
    """Модель промокода."""

    code = models.CharField(
        _("Промокод"),
        max_length=50,
        unique=True
    )
    discount = models.PositiveSmallIntegerField(
        _("Скидка в %"),
    	validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    valid_from = models.DateTimeField(
        _("Действителен с"),
        db_index=True
    )
    valid_to = models.DateTimeField(
        _("Действителен до"),
        db_index=True
    )
    is_active = models.BooleanField(
        _("Активен"),
    	default=True,
        db_index=True
    )

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    def is_valid(self) -> bool:
        """Проверяет, активен ли промокод и действует ли он по времени."""
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to


class Order(models.Model):
    """Модель заказа подписки."""

    class DurationChoices(models.IntegerChoices):
        ONE_MONTH = 1, _("1 месяц")
        THREE_MONTHS = 3, _("3 месяца")
        SIX_MONTHS = 6, _("6 месяцев")
        TWELVE_MONTHS = 12, _("12 месяцев")

    class PersonsChoices(models.IntegerChoices):
        ONE = 1, _("1 персона")
        TWO = 2, _("2 персоны")
        THREE = 3, _("3 персоны")
        FOUR = 4, _("4 персоны")
        FIVE = 5, _("5 персон")
        SIX = 6, _("6 персон")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Пользователь")
    )
    menu_type = models.ForeignKey(
        "menu.Menu",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Тип меню")
    )

    duration = models.IntegerField(
        _("Срок подписки (мес)"),
        choices=DurationChoices.choices,
        default=DurationChoices.ONE_MONTH
    )
    persons_count = models.IntegerField(
        _("Количество персон"),
        choices=PersonsChoices.choices,
        default=PersonsChoices.ONE
    )

    has_breakfast = models.BooleanField(_("Завтраки"), default=True)
    has_lunch = models.BooleanField(_("Обеды"), default=True)
    has_dinner = models.BooleanField(_("Ужины"), default=True)
    has_dessert = models.BooleanField(_("Десерты"), default=True)

    excluded_allergens = models.ManyToManyField(
        "menu.Allergen",
        blank=True,
        related_name="orders_excluded",
        verbose_name=_("Исключенные аллергены")
    )

    total_price = models.DecimalField(_("Стоимость"), max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True, db_index=True)
    is_paid = models.BooleanField(_("Оплачен"), default=False, db_index=True)
    is_active = models.BooleanField(_("Активен"), default=True, db_index=True)

    promocode = models.ForeignKey(
    	"orders.PromoCode",
    	null=True,
    	blank=True,
    	on_delete=models.SET_NULL,
    	related_name="orders",
    	verbose_name=_("Промокод")
    )

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Заказ №{self.id} — {self.user.email}"

    def calculate_price(self) -> Decimal:
        """Рассчитывает полную стоимость подписки за весь срок."""
        prices_per_day = {"breakfast": 200, "lunch": 300, "dinner": 400, "dessert": 100}
        modifiers = {1: 1.0, 3: 1.6, 6: 1.8, 12: 2.0}

        base_daily_price = sum([
            prices_per_day["breakfast"] if self.has_breakfast else 0,
            prices_per_day["lunch"] if self.has_lunch else 0,
            prices_per_day["dinner"] if self.has_dinner else 0,
            prices_per_day["dessert"] if self.has_dessert else 0,
        ])

        monthly_base_price = Decimal(base_daily_price) * Decimal(30)
        modifier = modifiers.get(self.duration, float(self.duration))

        base_total_price = monthly_base_price * Decimal(modifier) * Decimal(self.persons_count)

        if self.promocode and self.promocode.is_valid():
            discount = Decimal(self.promocode.discount)
            return (base_total_price * (Decimal(100) - discount) / Decimal(100)).quantize(Decimal("0.01"))
        return base_total_price.quantize(Decimal("0.01"))

    def get_ration_for_date(self, target_date):
        """Достает сохраненный рацион из DailyRation на конкреиную дату."""
        from apps.menu.models import Recipe

        ration_obj = self.daily_rations.filter(date=target_date).first()

        if not ration_obj:
            return {"ration": {}, "calories": 0}

        ration_dict = {}
        if ration_obj.breakfast:
            ration_dict[Recipe.MealTypes.BREAKFAST] = ration_obj.breakfast
        if ration_obj.lunch:
            ration_dict[Recipe.MealTypes.LUNCH] = ration_obj.lunch
        if ration_obj.dinner:
            ration_dict[Recipe.MealTypes.DINNER] = ration_obj.dinner
        if ration_obj.dessert:
            ration_dict[Recipe.MealTypes.DESSERT] = ration_obj.dessert

        return {"ration": ration_dict, "calories": ration_obj.total_calories}

    def save(self, *args, **kwargs):
        """Считает цену и генерирует рацион при первом создании."""
        is_new = self.pk is None

        if not self.total_price:
            self.total_price = self.calculate_price()
        super().save(*args, **kwargs)

        if is_new:
            from .services import OrderRationService
            OrderRationService.generate_rations_for_order(self)


class DailyRation(models.Model):
    """Модель для генерации неизменяемого рацион на конкретный день."""

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="daily_rations",
        verbose_name=_("Заказ")
    )
    date = models.DateField(_("Дата рациона"), db_index=True)

    breakfast = models.ForeignKey("menu.Recipe", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    lunch = models.ForeignKey("menu.Recipe", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    dinner = models.ForeignKey("menu.Recipe", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    dessert = models.ForeignKey("menu.Recipe", on_delete=models.PROTECT, null=True, blank=True, related_name="+")

    total_calories = models.PositiveIntegerField(_("Всего калорий"), default=0)

    class Meta:
        verbose_name = _("Дневной рацион")
        verbose_name_plural = _("Дневные рационы")
        unique_together = ("order", "date")

    def __str__(self):
        return f"Рацион заказа №{self.order.id} на {self.date}"
