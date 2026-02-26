from django.db import models
from django.contrib.auth.models import User

# orders/models.py
from django.db import models
from django.contrib.auth.models import User


# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from products.models import Product  # adjust import path
import random

def generate_order_number():
    return random.randint(100000000, 999999999)
class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        null=True,
        blank=True
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="United States")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.city}"



from django.db import models
from django.contrib.auth.models import User


# orders/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User


# orders/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):

    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    )

    ORDER_STATUS = (
        ("PLACED", "Order Placed"),
        ("CONFIRMED", "Confirmed"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="orders",
        null=True, blank=True
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        null=True, blank=True
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    public_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    order_number = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.order_number:
            while True:
                number = random.randint(100000000, 999999999)
                if not Order.objects.filter(order_number=number).exists():
                    self.order_number = number
                    break
        super().save(*args, **kwargs)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ ADD

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="PENDING"
    )

    order_status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS,
        default="PLACED"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username if self.user else 'Guest'}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(   # 👈 ADD THIS
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product_name = models.CharField(max_length=255)
    product_image = models.URLField()   # snapshot image URL
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.product_name
class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    status = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} - {self.status}"
