from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls", namespace="pages")),
    path("menu/", include("apps.menu.urls", namespace="menu")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
