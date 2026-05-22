from django.contrib import admin

from .models import Order, DailyRation, PromoCode
from .services import OrderRationService


class DailyRationInline(admin.TabularInline):
    """Отображает список дней меню внутри страницы заказа."""

    model = DailyRation
    extra = 0
    raw_id_fields = ("breakfast", "lunch", "dinner", "dessert")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов."""

    list_display = ("id", "user", "total_price", "is_active", "is_paid", "created_at")
    list_filter = ("is_paid", "is_active", "duration", "menu_type", "created_at")
    search_fields = ("id", "user__email", "promocode__code")
    filter_horizontal = ("excluded_allergens",)
    readonly_fields = ("total_price",)
    list_display_links = ("user",)

    inlines = [DailyRationInline]

    actions = ["regenerate_menu"]

    @admin.action(description="Перегенерировать меню для выбранных заказов.")
    def regenerate_menu(self, request, queryset):
        for order in queryset:
            OrderRationService.generate_rations_for_order(order)
        self.message_user(request, "Меню успешно перегенерировано.")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    """Админка для промокодов."""

    list_display = ("code", "discount", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("code",)


@admin.register(DailyRation)
class DailyRationAdmin(admin.ModelAdmin):
    """Админка для отдельных дней рациона (если нужно найти конкретный день)."""

    list_display = ("date", "order", "total_calories", "breakfast", "lunch", "dinner", "dessert")
    list_filter = ("date",)
    search_fields = ("order__id", "order__user__email")
    raw_id_fields = ("order", "breakfast", "lunch", "dinner", "dessert")
