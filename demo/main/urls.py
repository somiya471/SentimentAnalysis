from django.contrib import admin
from django.urls import path
from . import views




urlpatterns = [
    path('',views.home,name="mainHome"),
    path('contact',views.contact,name="contact"),
    path('predict',views.predict,name="predict"),
    path('aboutus',views.aboutus,name="aboutus"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('load_data',views.load_data,name="load_data"),
    path('loginpage',views.loginpage,name="loginpage"),
    path('logoutpage',views.logoutpage,name="logoutpage"),
    path('register',views.register,name="register"),
    # path('dataset',views.dataset,name="dataset"),
    # path('inputcsv', views.inputcsv, name="inputcsv"),
    path('submit',views.submit,name="submit"),
]