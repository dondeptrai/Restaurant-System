from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('testing/', views.testing, name='testing'),
    path('register/', views.register, name='register'),
   path('login/', views.login, name='login'),
    
]
