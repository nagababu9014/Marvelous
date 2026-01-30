from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView

from cart.models import CartItem
from cart.serializers import CartItemSerializer
from cart.utils import get_cart


# -----------------------------
# ADD TO CART
# -----------------------------
class AddToCartAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product is required"}, status=400)

        cart = get_cart(
            user=request.user,
            guest_id=request.headers.get("X-GUEST-ID"),
            create=True
        )

        if not cart:
            return Response({"error": "Cart closed"}, status=400)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({"message": "Item added"}, status=201)


# -----------------------------
# LIST CART ITEMS
# -----------------------------
class CartItemListAPIView(ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart = get_cart(
            user=self.request.user,
            guest_id=self.request.headers.get("X-GUEST-ID")
        )

        if not cart:
            return CartItem.objects.none()

        return CartItem.objects.filter(cart=cart)


# -----------------------------
# UPDATE CART ITEM
# -----------------------------
class UpdateCartItemAPIView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        quantity = int(request.data.get("quantity", 1))

        cart = get_cart(
            user=request.user,
            guest_id=request.headers.get("X-GUEST-ID")
        )

        if not cart:
            return Response({"error": "Cart not found"}, status=404)

        try:
            item = CartItem.objects.get(pk=pk, cart=cart)
            item.quantity = quantity
            item.save()
            return Response({"message": "Quantity updated"})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)


# -----------------------------
# REMOVE CART ITEM
# -----------------------------
class RemoveCartItemAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        cart = get_cart(
            user=request.user,
            guest_id=request.headers.get("X-GUEST-ID")
        )

        if not cart:
            return Response({"error": "Cart not found"}, status=404)

        try:
            item = CartItem.objects.get(pk=pk, cart=cart)
            item.delete()
            return Response({"message": "Item removed"})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)


# -----------------------------
# CHECKOUT (USER ONLY)
# -----------------------------
class CheckoutAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 🔒 Only logged-in users can checkout
        if not request.user.is_authenticated:
            return Response(
                {"error": "Login required"},
                status=401
            )

        cart = get_cart(user=request.user)

        if not cart:
            return Response({"items": [], "total_amount": 0})

        items = CartItem.objects.filter(cart=cart)

        total = 0
        data = []

        for item in items:
            subtotal = item.product.price * item.quantity
            total += subtotal
            data.append({
                "product": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": subtotal
            })

        return Response({
            "items": data,
            "total_amount": total
        })
