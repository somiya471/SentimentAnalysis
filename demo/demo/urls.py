"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path,include
from . import views




urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('main.urls')),
    path('predict',include('main.urls')),
    path('submit',include('main.urls')),
    path('dashboard',include('main.urls')),
    # path('inputcsv',include('main.urls')),
    path('load_data',include('main.urls')),
    path('loginpage',include('main.urls')),
    path('logoutpage',include('main.urls')),
    path('register',include('main.urls')),
    # path('dataset',include('main.urls')),
    path('contact',include('main.urls')),
    path('aboutus',include('main.urls')),
    #path('dashboard',views.dashboard,name='dashboard'),

]
