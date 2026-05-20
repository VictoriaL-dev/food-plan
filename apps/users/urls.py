from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("registration", views.RegisterView.as_view(), name="register"),
    path("login", views.CustomLoginView.as_view(), name="login"),
    path("logout", views.CustomLogoutView.as_view(), name="logout"),
    path("profile", views.ProfileEditView.as_view(), name="profile"),

    path("password-reset/", views.CustomPasswordResetView.as_view(), name="reset-password"),
    path("password-reset/done/", views.CustomPasswordResetDoneView.as_view(), name="reset-done"),
    path("reset/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(), name="reset-confirm"),
    path("reset/done/", views.CustomPasswordResetCompleteView.as_view(), name="reset-complete"),
]
