"""
URL configuration for elda project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.defaults import page_not_found
from xel import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data_elda/', include('data_elda.urls')),
    path('xel/', include('xel.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    
    # In your_project/urls.py
    path('health_check/', views.health_check),
]

handler404 = lambda request, exception: views.health_check(request) if request.path == '/health_check/' else page_not_found(request, exception)