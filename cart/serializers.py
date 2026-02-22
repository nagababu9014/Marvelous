from rest_framework import serializers
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    product_image = serializers.SerializerMethodField()

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
            "product",
            "product_id",
            "product_category",
            "quantity",
            "product_name",
            "product_price",
            "product_image",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")

        first_image = obj.product.images.first()
        if first_image and first_image.image:
            return request.build_absolute_uri(first_image.image.url)

        return None