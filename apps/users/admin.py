from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""

    list_display = ("email", "first_name", "is_active", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email",)
    ordering = ("email",)
    list_editable = ("is_active",)
    readonly_fields = ("get_avatar_preview",)

    fieldsets = (
        (_("Персональная информация"), {"fields": ("get_avatar_preview", "avatar", "first_name", "email", "password")}),
        (
            _("Права доступа"),
            {
                "classes": ("collapse",),
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
        (_("Даты"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "email",
                    "password1",
                    "password1",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    def get_avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="45" height="45" style="object-fit: cover; border-radius: 50%;"/>')
        return _("Нет фото")

    get_avatar_preview.short_description = _("Аватарка")
