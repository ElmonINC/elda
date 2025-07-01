# xel/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_xel, name='admin'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('search/', views.search_narration, name='search_narration'),
]