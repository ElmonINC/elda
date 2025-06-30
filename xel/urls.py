# xel/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_xel, name='upload_xel'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('search/', views.search_name, name='search_name'),
]