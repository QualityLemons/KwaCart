from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def home(request):
    return redirect('tools:catalog' if request.user.is_authenticated else 'accounts:login')


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('tools/', include('tools.urls')),
    path('archive/', include('archive.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
