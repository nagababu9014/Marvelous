# orders/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from cart.models import CartItem
from cart.utils import get_cart
from .models import Order, Address,OrderStatusHistory
from .models import OrderItem
from backend.authentication import CsrfExemptSessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class CreateOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ✅ FIX: pass user & guest_id correctly (NOT request)
        cart = get_cart(
            user=request.user,
            guest_id=request.headers.get("X-GUEST-ID")
        )

        if not cart:
            return Response({"error": "Cart expired"}, status=400)

        items = CartItem.objects.filter(cart=cart)
        if not items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        address_id = request.data.get("address_id")
        if not address_id:
            return Response({"error": "Address required"}, status=400)

        try:
            address = Address.objects.get(
                id=address_id,
                user=request.user
            )
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=404)

        total = sum(
            item.product.price * item.quantity
            for item in items
        )

        # ✅ ALWAYS CREATE NEW ORDER
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
            payment_status="PENDING",
            order_status="PLACED",
            session_key=request.session.session_key
        )

        OrderStatusHistory.objects.create(
            order=order,
            status="PLACED"
        )

        request_scheme = request.scheme
        request_host = request.get_host()

        for item in items:
            image_url = ""
            if item.product.image:
                image_url = (
                    f"{request_scheme}://{request_host}"
                    f"{item.product.image.url}"
                )

            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                product_image=image_url,
                price=item.product.price,
                quantity=item.quantity
            )

        return Response({
            "order_id": order.id,
            "order_token": str(order.public_token),
            "total_amount": order.total_amount,
            "payment_status": order.payment_status,
            "order_status": order.order_status
        })


class OrderByTokenAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, token):
        try:
            order = Order.objects.select_related(
                "address"
            ).prefetch_related("items").get(
                public_token=token
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        address = order.address     
        return Response({
            "id": order.id,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "total_amount": order.total_amount,
            "created_at": order.created_at,

            "address": {
                "first_name": address.first_name,
                "last_name": address.last_name,
                "phone": address.phone,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "state": address.state,
                "zip_code": address.zip_code,
            },
            "items": [
                {
                    "name": item.product_name,
                    "image": item.product_image,
                    "price": item.price,
                    "quantity": item.quantity
                }
                for item in order.items.all()
            ]
        })

class MyOrdersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        orders = Order.objects.filter(
            user=request.user,
            payment_status="PAID"
        ).order_by("-created_at")


        return Response([
            {
                "id": o.id,
                "order_token": str(o.public_token),
                "total_amount": o.total_amount,
                "payment_status": o.payment_status,
                "order_status": o.order_status,
                "created_at": o.created_at,

                "items": [
                    {
                        "name": i.product_name,
                        "image": i.product_image,
                        "price": i.price,
                        "quantity": i.quantity
                    }
                    for i in o.items.all()
                ]
            }
            for o in orders
        ])

from rest_framework.permissions import IsAuthenticated

class SaveAddressAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data

        address = Address.objects.create(
            user=request.user,
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
            address_line1=data["address_line1"],
            address_line2=data.get("address_line2", ""),
            city=data["city"],
            state=data["state"],
            zip_code=data["zip_code"],
        )

        return Response({
            "message": "Address saved",
            "address_id": address.id
        })

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

class AddressListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)

        return Response([
            {
                "id": a.id,
                "first_name": a.first_name,
                "last_name": a.last_name,
                "phone": a.phone,
                "address_line1": a.address_line1,
                "address_line2": a.address_line2,
                "city": a.city,
                "state": a.state,
                "zip_code": a.zip_code,
            }
            for a in addresses
        ])


from rest_framework.permissions import IsAuthenticated

class SelectAddressAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        address_id = request.data.get("address_id")

        try:
            Address.objects.get(
                id=address_id,
                user=request.user
            )
        except Address.DoesNotExist:
            return Response(
                {"error": "Address not found"},
                status=404
            )

        # ✅ nothing stored in session
        return Response({"message": "Address valid"})
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order

class OrderTrackingAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.prefetch_related(
                "status_history"
            ).get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )

        return Response({
            "order_id": order.id,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "tracking": [
                {
                    "status": h.status,
                    "time": h.updated_at
                }
                for h in order.status_history.all().order_by("updated_at")
            ]
        })
