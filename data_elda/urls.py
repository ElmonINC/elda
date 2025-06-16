from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Add your URL patterns here
    # Example: path('', views.home, name='home'),
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('search/', views.search, name='search'),
]
# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)