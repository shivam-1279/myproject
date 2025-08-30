# admin.py
from django.contrib import admin
from .models import Category, Item, CartItem, Order, OrderItem, Reservation

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Reservation)