# urls.py
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Core Pages
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    
    # Authentication
    path('register/', views.register, name='register'),
    
    # Cart System
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # Order System
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]