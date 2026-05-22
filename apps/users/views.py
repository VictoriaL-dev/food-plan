import datetime

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from .models import CustomUser
from apps.orders.models import Order
from .forms import (
    RegistrationForm,
    LoginForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    ProfileEditForm
)


class RegisterView(UserPassesTestMixin, CreateView):
    """Контроллер для регистрации новых пользователей.

    Рендерит страницу регистрации, автоматически логинит
    пользователя после успеха и отправляет его в личный кабинет.
    """

    model = CustomUser
    form_class = RegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:profile")
    login_url = reverse_lazy("users:profile")

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(self.login_url)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomLoginView(UserPassesTestMixin, LoginView):
    """Контроллер для авторизации существующих пользователей.

    Рендерит страницу логина и использует кастомную форму
    аутентификации с логином по Email. После успешного входа
    перенаправляет пользователя в Личный кабинет.
    """

    form_class = LoginForm
    template_name = "users/auth.html"
    login_url = reverse_lazy("users:profile")

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(self.login_url)

    def get_success_url(self) -> str:
        return reverse_lazy("users:profile")


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    """Контроллер для выхода пользователя из системы."""

    next_page = reverse_lazy("pages:index")
    login_url = reverse_lazy("users:login")


# class ProfileEditView(LoginRequiredMixin, UpdateView):
#     """Контроллер Личного кабинета."""
#
#     form_class = ProfileEditForm
#     template_name = "users/lk.html"
#
#     def get(self, request, *args, **kwargs):
#         """Отображает страницу личного кабинета с предзаполненной формой."""
#         form = self.form_class(instance=request.user)
#         context = {
#             "form": form,
#             "has_subscription": True,
#             "is_profile": True
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, *args, **kwargs):
#         """Обрабатывает сохранение данных профиля или загрузку аватарки."""
#         form = self.form_class(request.POST, request.FILES, instance=request.user)
#
#         if form.is_valid():
#             is_avatar_change = "avatar" in request.FILES
#             user = form.save()
#             update_session_auth_hash(request, user)
#
#             if is_avatar_change:
#                 messages.success(request, "Фото профиля успешно обновлено!")
#             else:
#                 messages.success(request, "Персональные данные успешно обновлены!")
#
#             return redirect("users:profile")
#
#         context = {
#             "form": form,
#             "has_subscription": True,
#             "is_profile": True
#         }
#         return render(request, self.template_name, context)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Контроллер Личного кабинета с выводом информации о профиле и подписке."""

    form_class = ProfileEditForm
    template_name = "users/lk.html"

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя для UpdateView."""
        return self.request.user

    def get_order_context(self, user):
        """Вспомогательный метод для получения данных о подписке и меню на сегодня."""
        active_order = Order.objects.filter(
            user=user,
            is_paid=True,
            is_active=True
        ).select_related('menu_type').prefetch_related('excluded_allergens').last()

        if not active_order:
            return {"has_subscription": False, "order": None, "today_ration": {}, "today_calories": 0, "meals_count": 0}

        today_date = datetime.date.today()
        ration_data = active_order.get_ration_for_date(today_date)
        meals_count = len(ration_data["ration"])

        return {
            "has_subscription": True,
            "order": active_order,
            "today_ration": ration_data["ration"],
            "today_calories": ration_data["calories"],
            "meals_count": meals_count
        }

    def get(self, request, *args, **kwargs):
        """Отображает страницу личного кабинета."""
        form = self.form_class(instance=request.user)
        order_context = self.get_order_context(request.user)

        context = {
            "form": form,
            "is_profile": True,
            "active_tab": "profile",
            **order_context
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Обрабатывает сохранение данных профиля."""
        form = self.form_class(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            is_avatar_change = "avatar" in request.FILES
            user = form.save()
            update_session_auth_hash(request, user)

            if is_avatar_change:
                messages.success(request, "Фото профиля успешно обновлено!")
            else:
                messages.success(request, "Персональные данные успешно обновлены!")

            return redirect("users:profile")

        order_context = self.get_order_context(request.user)
        context = {
            "form": form,
            "is_profile": True,
            "active_tab": "profile",
            **order_context
        }
        return render(request, self.template_name, context)


class CustomPasswordResetView(PasswordResetView):
    """Контроллер отправки ссылки для восстановления пароля."""
    form_class = CustomPasswordResetForm
    template_name = "users/password_reset/request-form.html"
    email_template_name = "users/password_reset/email.html"
    success_url = reverse_lazy("users:reset-done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Контроллер страницы уведомления об отправке письма."""
    template_name = "users/password_reset/done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Контроллер проверки токена и ввода нового пароля."""
    form_class = CustomSetPasswordForm
    template_name = "users/password_reset/confirm-form.html"
    success_url = reverse_lazy("users:reset-complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Контроллер страницы успешного завершения сброса пароля."""
    template_name = "users/password_reset/complete.html"
