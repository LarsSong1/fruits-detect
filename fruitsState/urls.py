from django.urls import path
from .views import Home, Register, Login, Logout, DetectFruits, Inventory

urlpatterns = [
    path('', Home, name='home'), 
    path('login/', Login, name='login'),
    path('register/', Register, name='register'), 
    path('logout/', Logout, name='logout'),
    path('detectFruits/', DetectFruits.as_view(), name='detect-fruits'),
    path('inventory/', Inventory, name='inventory'),
]
