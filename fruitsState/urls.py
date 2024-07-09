from django.urls import path
from .views import Home, Register, Login, Logout, DetectFruits, Inventory, EditDetectFruits, DeleteRegisterFruit, Clasification

urlpatterns = [
    path('', Home, name='home'), 
    path('login/', Login, name='login'),
    path('register/', Register, name='register'), 
    path('logout/', Logout, name='logout'),
    path('detectFruits/', DetectFruits.as_view(), name='detect-fruits'),
    path('edit-detected-fruits/<int:pk>/', EditDetectFruits.as_view(), name='edit-fruits'),
    path('delete-fruit/<int:user_id>/', DeleteRegisterFruit, name='delete-fruit'),
    path('inventory/<int:user_id>/', Inventory, name='inventory'),
    path('clasification/<int:user_id>/', Clasification, name='clasification')
]


