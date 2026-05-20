import os

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_delete, pre_save
from django.contrib.auth.models import BaseUserManager, AbstractUser


def validate_avatar_size(fieldfile_obj):
    """Проверяет, чтобы вес файла не превышал лимит из настроек проекта."""
    max_mb = getattr(settings, "AVATAR_MAX_SIZE_MB", 2)

    if fieldfile_obj.size > max_mb * 1024 * 1024:
        raise ValidationError(
            _(f"Максимальный размер файла — {max_mb} МБ.")
        )


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя.

    Использует Email в качестве уникального идентификатора для авторизации
    вместо стандартного Username.
    """

    def _create_user(self, first_name: str, email: str, password: str | None, **extra_fields) -> "CustomUser":
        """Внутренний метод для создания и сохранения пользователя в базе данных.

        Args:
            first_name: Имя пользователя.
            email: Электронная почта пользователя.
            password: Пароль пользователя (или None для неиспользуемого пароля).
            **extra_fields: Дополнительные необязательные поля модели.

        Returns:
            CustomUser: Созданный объект пользователя.

        Raises:
            ValueError: Если не передан email или first_name.
        """
        if not email:
            raise ValueError(_("Электронная почта должна быть указана."))
        if not first_name:
            raise ValueError(_("Имя пользователя должно быть указано."))

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, first_name: str, email: str, password: str | None = None, **extra_fields) -> "CustomUser":
        """Создает и возвращает обычного пользователя.

        Args:
            first_name: Имя пользователя.
            email: Электронная почта пользователя.
            password: Пароль пользователя. По умолчанию None.
            **extra_fields: Дополнительные необязательные поля модели.

        Returns:
            CustomUser: Созданный объект обычного пользователя.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, first_name, **extra_fields)

    def create_superuser(self, first_name: str, email: str, password: str, **extra_fields) -> "CustomUser":
        """Создает и возвращает суперпользователя с правами администратора.

        Args:
            first_name: Имя суперпользователя.
            email: Электронная почта суперпользователя.
            password: Пароль суперпользователя.
            **extra_fields: Дополнительные необязательные поля модели.

        Returns:
            CustomUser: Созданный объект суперпользователя.

        Raises:
            ValueError: Если флаги is_staff или is_superuser установлены в False.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Суперпользователь должен иметь is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Суперпользователь должен иметь is_superuser=True."))

        return self._create_user(first_name, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя.

    Удаляет поля `username` и `last_name`, делая авторизацию по `email`,
    и хранит только имя пользователя в `first_name`.

    Attributes:
        email: Уникальный адрес электронной почты.
        first_name: Обязательное поле для имени пользователя.
        avatar: Изображение профиля пользователя.
    """

    username = None
    last_name = None

    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("Имя"), max_length=150, blank=False, null=False)
    avatar = models.ImageField(
        _("Аватарка"),
        upload_to="users/avatars/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            validate_avatar_size
        ]
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self) -> str:
        return str(self.email)


@receiver(post_delete, sender=CustomUser)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Удаляет аватарку с диска при удалении профиля пользователя."""
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)


@receiver(pre_save, sender=CustomUser)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Удаляет старую аватарку с диска при загрузке новой."""
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).avatar
    except sender.DoesNotExist:
        return False

    new_file = instance.avatar
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
    return None
