from rest_framework import serializers
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    # ✅ EXISTING FIELDS (UNCHANGED)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_image = serializers.ImageField(
        source="product.image",
        read_only=True
    )

    # ✅ NEW FIELDS (ADDED, NOT REPLACING ANYTHING)
    product_id = serializers.IntegerField(
        source="product.id", read_only=True
    )
    product_category = serializers.IntegerField(
        source="product.category.id", read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",          # 🔥 unchanged (important)
            "product_id",       # ✅ added
            "product_category", # ✅ added
            "quantity",
            "product_name",
            "product_price",
            "product_image",
        ]
