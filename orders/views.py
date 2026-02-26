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
from decimal import Decimal

US_STATE_TAX_RATES = {
    "AL": Decimal("0.04"),
    "AK": Decimal("0.00"),
    "AZ": Decimal("0.056"),
    "AR": Decimal("0.065"),
    "CA": Decimal("0.0725"),
    "CO": Decimal("0.029"),
    "CT": Decimal("0.0635"),
    "DE": Decimal("0.00"),
    "FL": Decimal("0.06"),
    "GA": Decimal("0.04"),
    "HI": Decimal("0.04"),
    "ID": Decimal("0.06"),
    "IL": Decimal("0.0625"),
    "IN": Decimal("0.07"),
    "IA": Decimal("0.06"),
    "KS": Decimal("0.065"),
    "KY": Decimal("0.06"),
    "LA": Decimal("0.0445"),
    "ME": Decimal("0.055"),
    "MD": Decimal("0.06"),
    "MA": Decimal("0.0625"),
    "MI": Decimal("0.06"),
    "MN": Decimal("0.06875"),
    "MS": Decimal("0.07"),
    "MO": Decimal("0.04225"),
    "MT": Decimal("0.00"),
    "NE": Decimal("0.055"),
    "NV": Decimal("0.0685"),
    "NH": Decimal("0.00"),
    "NJ": Decimal("0.06625"),
    "NM": Decimal("0.05125"),
    "NY": Decimal("0.04"),
    "NC": Decimal("0.0475"),
    "ND": Decimal("0.05"),
    "OH": Decimal("0.0575"),
    "OK": Decimal("0.045"),
    "OR": Decimal("0.00"),
    "PA": Decimal("0.06"),
    "RI": Decimal("0.07"),
    "SC": Decimal("0.06"),
    "SD": Decimal("0.045"),
    "TN": Decimal("0.07"),
    "TX": Decimal("0.0625"),
    "UT": Decimal("0.0485"),
    "VT": Decimal("0.06"),
    "VA": Decimal("0.043"),
    "WA": Decimal("0.065"),
    "WV": Decimal("0.06"),
    "WI": Decimal("0.05"),
    "WY": Decimal("0.04"),
}
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

        subtotal = sum(
        item.product.price * item.quantity
        for item in items
        )

        # ✅ Get state tax rate
        state_code = (address.state or "").strip().upper()
        tax_rate = US_STATE_TAX_RATES.get(state_code, Decimal("0.05"))  # default 5%

        tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))

        final_total = (subtotal + tax_amount).quantize(Decimal("0.01"))

        # ✅ ALWAYS CREATE NEW ORDER
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=final_total,
            tax_amount=tax_amount,
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

            first_image = item.product.images.first()

            if first_image and first_image.image:
                image_url = request.build_absolute_uri(
                    first_image.image.url
                )

            OrderItem.objects.create(
                order=order,
                product=item.product,  # 👈 ADD THIS
                product_name=item.product.name,
                product_image=image_url,
                price=item.product.price,
                quantity=item.quantity
            )

        return Response({
            "order_id": order.id,
                "order_number": order.order_number,   # ✅ ADD THIS

            "order_token": str(order.public_token),
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_amount": final_total,
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

            # ✅ ADD THESE
            "subtotal": str(order.total_amount - order.tax_amount),
            "tax_amount": str(order.tax_amount),
            "total_amount": str(order.total_amount),

            "created_at": order.created_at,

            "address": {
                "first_name": address.first_name,
                "last_name": address.last_name,
                "email": address.email,
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
                    "price": str(item.price),
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
                "order_number": o.order_number,   # ADD THIS
                "order_token": str(o.public_token),
                "total_amount": o.total_amount,
                "payment_status": o.payment_status,
                "order_status": o.order_status,
                "created_at": o.created_at,

                "items": [
                    {    "product_id": i.product.id if i.product else None,
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

        if not data.get("phone"):
            return Response({"error": "Phone is required"}, status=400)

        if not request.user.email:
            return Response(
                {"error": "User email not set"},
                status=400
            )

        address = Address.objects.create(
            user=request.user,
            first_name=data["first_name"],   # editable
            last_name=data["last_name"],     # editable
            email=request.user.email,        # fixed
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
                "email": a.email,  # ✅ ADD

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
