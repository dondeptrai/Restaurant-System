from django.urls import path
from . import views
from .views import add_order

urlpatterns = [
    path('', views.main, name='main'),
    path('testing/', views.testing, name='testing'),
    path('search/', views.search_orders, name='search_orders'),
    path('add_order/', add_order, name='add_order'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),


]
