from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order

from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "price", "quantity")


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("status", "updated_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_amount",
        "payment_status",
        "order_status",
        "created_at",
    )

    list_filter = ("payment_status", "order_status", "created_at")
    search_fields = ("id", "user__username", "user__email")

    readonly_fields = (
        "public_token",
        "created_at",
    )

    inlines = [OrderItemInline, OrderStatusHistoryInline]

    def save_model(self, request, obj, form, change):
        """
        Automatically add tracking history
        when order_status is changed from admin
        """
        if change:
            old_obj = Order.objects.get(pk=obj.pk)
            if old_obj.order_status != obj.order_status:
                OrderStatusHistory.objects.create(
                    order=obj,
                    status=obj.order_status
                )

        super().save_model(request, obj, form, change)
