import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripePaymentIntent(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # smallest unit
            currency="inr",
            metadata={
                "order_id": str(order.id)  # 🔥 MUST be string
            }
        )


        return Response({
            "client_secret": intent.client_secret
        })
