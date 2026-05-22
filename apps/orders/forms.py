from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import PromoCode, Order
from apps.menu.models import Allergen


class OrderForm(forms.ModelForm):
    BOOLEAN_SELECT_CHOICES = [
        (True, _("✔")),
        (False, _("✖")),
    ]

    has_breakfast = forms.TypedChoiceField(
        choices=BOOLEAN_SELECT_CHOICES,
        coerce=lambda val: val == "True" or val is True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Завтраки")
    )
    has_lunch = forms.TypedChoiceField(
        choices=BOOLEAN_SELECT_CHOICES,
        coerce=lambda val: val == "True" or val is True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Обеды")
    )
    has_dinner = forms.TypedChoiceField(
        choices=BOOLEAN_SELECT_CHOICES,
        coerce=lambda val: val == "True" or val is True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Ужины")
    )
    has_dessert = forms.TypedChoiceField(
        choices=BOOLEAN_SELECT_CHOICES,
        coerce=lambda val: val == "True" or val is True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Десерты")
    )

    excluded_allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input me-1 foodplan_checked-green"}),
        required=False,
        label=_("Аллергии")
    )

    promocode_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Введите промокод")}),
        label=_("Промокод")
    )

    class Meta:
        model = Order
        fields = [
            "menu_type", "duration", "has_breakfast", "has_lunch",
            "has_dinner", "has_dessert", "persons_count",
            "excluded_allergens"
        ]
        widgets = {
            "menu_type": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "duration": forms.Select(attrs={"class": "form-select"}),
            "has_breakfast": forms.Select(attrs={"class": "form-select"}),
            "has_lunch": forms.Select(attrs={"class": "form-select"}),
            "has_dinner": forms.Select(attrs={"class": "form-select"}),
            "has_dessert": forms.Select(attrs={"class": "form-select"}),
            "persons_count": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["duration"].empty_label = None
        self.fields["persons_count"].empty_label = None

    def clean_promocode_code(self):
        """Проверяет существование, активность и срок действия промокода, а также
        делает невозможным повторный ввод для одного и того же пользователя."""
        code = self.cleaned_data.get("promocode_code")
        if not code:
            return None

        promo = PromoCode.objects.filter(code=code).first()
        if not promo:
            raise ValidationError(_("Такого промокода не существует."))

        if not promo.is_valid():
            raise ValidationError(_("Срок действия этого промокода истек или он больше неактивен."))

        if self.user and Order.objects.filter(user=self.user, promocode=promo).exists():
            raise ValidationError(_("Вы уже использовали этот промокод."))

        return promo

    def clean(self):
        """Проверяет наличие активного заказа и выбор хотя бы одного приема пищи."""
        cleaned_data = super().clean()

        if self.user and self.user.is_authenticated:
            active_subscription_exists = Order.objects.filter(
                user=self.user,
                is_active=True,
                is_paid=True
            ).exists()

            if active_subscription_exists:
                raise ValidationError(_("Вы не можете оформить новый заказ, пока у вас действует активная подписка."))

        has_breakfast = cleaned_data.get("has_breakfast")
        has_lunch = cleaned_data.get("has_lunch")
        has_dinner = cleaned_data.get("has_dinner")
        has_dessert = cleaned_data.get("has_dessert")

        if not any([has_breakfast, has_lunch, has_dinner, has_dessert]):
            raise ValidationError(_("Необходимо выбрать хотя бы один прием пищи (завтрак, обед, ужин или десерт)."))
        return cleaned_data

    def save(self, commit=True):
        """Связывает проверенный промокод с моделью заказа перед сохранением."""
        order = super().save(commit=False)

        promo = self.cleaned_data.get("promocode_code")
        if promo:
            order.promocode = promo

        if commit:
            order.save()
            self.save_m2m()
        return order
