from django.db import models
from django.utils import timezone

class Customer(models.Model):
    customer_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128, default='default_password')

    def __str__(self):
        return self.customer_name 

class RestaurantTable(models.Model):
    seat_num = models.IntegerField()
    location_seat = models.CharField(max_length=255,
                                     choices=[('main_dining', 'Main Dining Room'),
                                              ('outdoor', 'Outdoor'),
                                              ('rooftop', 'Rooftop')])
    status = models.CharField(max_length=50,
                              choices=[('available', 'Available'),
                                       ('reserved', 'Reserved')])

    def __str__(self):
        return f"Table {self.id} - {self.location_seat}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    numof_customer = models.IntegerField()
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Order {self.id} by {self.customer.customer_name}"

class OrderTable(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Order {self.order.id} - Table {self.table.id}"
    
    def check_and_update_table_status(self):
        current_time = timezone.now()
        
        if self.table.status == 'reserved' and current_time >= self.end_time:
            self.table.status = 'available'
            self.table.save()

            self.delete()

            remaining_order_tables = OrderTable.objects.filter(order=self.order)
            if not remaining_order_tables.exists():
                self.order.delete()
