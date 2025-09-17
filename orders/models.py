from django.db import models
import uuid

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id)

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', null=True, blank=True)
    is_available = models.BooleanField(default=True)  # New field for stock status

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('completed', 'Completed'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    table_number = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"Order {self.id} by {self.name}"

class OrderItem(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    )
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    preparation_time = models.IntegerField(null=True, blank=True)  # in minutes

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

class CompletedOrder(models.Model):
    order_id = models.IntegerField(unique=True)
    customer_id = models.UUIDField()
    name = models.CharField(max_length=100)
    table_number = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Completed Order {self.order_id} by {self.name}"

class CompletedOrderItem(models.Model):
    completed_order = models.ForeignKey(CompletedOrder, related_name='items', on_delete=models.CASCADE)
    menu_item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderItem.STATUS_CHOICES)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item_name}"