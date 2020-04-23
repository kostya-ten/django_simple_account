from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django_simple_account.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
