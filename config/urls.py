from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from config.views import custom_404_view, custom_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('', include('apps.authentication.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('uploads/', include('apps.uploads.urls')),
    path('influencers/', include('apps.influencers.urls')),
    
    # Development Error Page Preview Routes
    path('404/', custom_404_view, name='custom_404_preview'),
    path('500/', custom_500_view, name='custom_500_preview'),
]

# Serve media files and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom Error Handlers
handler404 = 'config.views.custom_404_view'
handler500 = 'config.views.custom_500_view'