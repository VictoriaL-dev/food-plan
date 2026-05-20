from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm

from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """Форма для регистрации нового пользователя.

    Запрашивает обязательные поля: имя, email и пароль. Автоматически
    хэширует пароль и проверяет его на надежность.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите e-mail",
                "id": "email",
                "aria-describedby": "emailHelp",
            },
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("first_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите имя",
                "id": "name",
            },
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите пароль",
                "id": "password",
            },
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Подтвердите пароль",
                "id": "PasswordConfirm",
            },
        )

    def clean_email(self) -> str:
        """Валидирует email: переводит в нижний регистр и проверяет на уникальность."""
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Этот Email уже зарегистрирован."))
        return email


class LoginForm(AuthenticationForm):
    """Форма для авторизации пользователя.

    Использует Email вместо стандартного Username в качестве логина.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите e-mail",
                "id": "email",
                "aria-describedby": "emailHelp",
            },
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите пароль",
                "id": "password",
            },
        )


class CustomPasswordResetForm(PasswordResetForm):
    """Форма запроса ссылки для восстановления пароля."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@email.com",
                "id": "email",
                "aria-describedby": "emailHelp",
            },
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Форма ввода нового пароля."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите новый пароль",
                "id": "password",
            },
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Подтвердите новый пароль",
                "id": "PasswordConfirm",
            },
        )


class ProfileEditForm(forms.ModelForm):
    """Форма профиля в Личном кабинете для редактирования данных и смены пароля.

    Поля Имя и Email предзаполнены. Поля паролей необязательны и
    заполняются только при необходимости изменить пароль.
    """

    new_password = forms.CharField(
        label=_("Пароль"),
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "password",
            }
        )
    )
    confirm_password = forms.CharField(
        label=_("Подтверждение пароля"),
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "PasswordConfirm",
            }
        )
    )

    class Meta:
        model = CustomUser
        fields = ("first_name", "email", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "id": "name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "id": "email"}),
            "avatar": forms.FileInput(attrs={"id": "avatar-input", "style": "display: none;", "onchange": "this.form.submit()"}),
        }

    def clean_email(self) -> str:
        """Проверяет уникальность email при его изменении."""
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("Этот Email уже занят другим пользователем."))
        return email

    def clean(self):
        """Проверяет совпадение паролей, если пользователь решил их заполнить."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password or confirm_password:
            if new_password != confirm_password:
                self.add_error("confirm_password", _("Новые пароли не совпадают."))
            try:
                validate_password(new_password, user=self.instance)
            except ValidationError as error:
                for msg in error.messages:
                    self.add_error("new_password", msg)
        return cleaned_data

    def save(self, commit=True):
        """Сохраняет профиль и меняет хэш пароля, если он был введен."""
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
        return user
