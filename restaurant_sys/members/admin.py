from django.contrib import admin
from .models import Customer, RestaurantTable, Order, OrderTable

admin.site.register(Customer)
admin.site.register(RestaurantTable)
admin.site.register(Order)
admin.site.register(OrderTable)