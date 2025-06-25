from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Add your URL patterns here
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('search/', views.search, name='search'),
    path('preview/<int:file_id>/', views.preview_file, name='preview_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
]
# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)