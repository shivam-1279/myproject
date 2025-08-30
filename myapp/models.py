from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="items/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 👇 Add this field
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-added_at']
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    @property
    def line_total(self):
        return self.item.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.item.name} in {self.user.username}'s cart"


class Order(models.Model):
    STATUS_CHOICES = [
        ('RECEIVED', 'Order Received'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Pickup/Delivery'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    items = models.ManyToManyField(
        Item,
        through='OrderItem',
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEIVED'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Price at time of ordering"
    )
    special_requests = models.TextField(blank=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    @property
    def line_total(self):
        return self.price_at_order * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.item.name} in Order #{self.order.id}"


class Reservation(models.Model):
    TIME_SLOTS = [
        ('17:00', '5:00 PM'),
        ('17:30', '5:30 PM'),
        ('18:00', '6:00 PM'),
        ('18:30', '6:30 PM'),
        ('19:00', '7:00 PM'),
        ('19:30', '7:30 PM'),
        ('20:00', '8:00 PM'),
        ('20:30', '8:30 PM'),
        ('21:00', '9:00 PM'),
    ]

    PARTY_SIZES = [
        (1, '1 person'),
        (2, '2 people'),
        (3, '3 people'),
        (4, '4 people'),
        (5, '5 people'),
        (6, '6+ people'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    date = models.DateField()
    time = models.CharField(max_length=5, choices=TIME_SLOTS)
    party_size = models.IntegerField(choices=PARTY_SIZES)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Reservation for {self.name} on {self.date} at {self.time}"
