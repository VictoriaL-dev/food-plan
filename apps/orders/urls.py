from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("make-order", views.CreateOrderView.as_view(), name="order"),
    path("check-promocode/", views.CheckPromoCodeView.as_view(), name="check_promocode")
]
