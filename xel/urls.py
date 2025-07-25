from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_xel, name='admin_xel'),
    path('admin/delete/<int:file_id>/', views.delete_excel_file, name='delete_excel_file'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('search/', views.search_narration, name='search_narration'),
    path('generate_pdf/<int:narration_id>/', views.generate_pdf_view, name='generate_pdf'),
]