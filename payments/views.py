# payments/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from orders.models import Order

class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response(
                {"error": "order_id required"},
                status=400
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )

        # ❌ NO PAYMENT LOGIC HERE
        # ❌ NO STATUS CHANGE
        # ❌ NO CART CLEAR

        return Response({
            "message": "Order validated",
            "order_id": order.id,
            "amount": order.total_amount,
            "status": order.status
        })
