import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from orders.models import Order, OrderStatusHistory
from cart.models import Cart
from payments.models import Payment
from payments.emails import (
    send_customer_order_mail,
    send_admin_order_mail
)

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    print("🔥 STRIPE WEBHOOK HIT")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # ✅ PAYMENT SUCCESS
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        stripe_payment_id = intent["id"]
        order_id = intent["metadata"].get("order_id")

        # 🔒 Idempotency check
        if Payment.objects.filter(payment_id=stripe_payment_id).exists():
            return JsonResponse({"status": "duplicate"})

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)

                if order.payment_status == "PAID":
                    return JsonResponse({"status": "already_paid"})

                # ✅ Save payment
                Payment.objects.create(
                    user=order.user,
                    order=order,
                    payment_id=stripe_payment_id,
                    payment_method="STRIPE",
                    amount=order.total_amount,
                    status="SUCCESS"
                )

                # ✅ Update order
                order.payment_status = "PAID"
                order.order_status = "CONFIRMED"
                order.save(update_fields=["payment_status", "order_status"])

                OrderStatusHistory.objects.create(
                    order=order,
                    status="CONFIRMED"
                )

                # 📧 SEND EMAILS (RIGHT PLACE ✅)
                if order.user and order.user.email:
                    send_customer_order_mail(order)

                send_admin_order_mail(order)

                # 🔥 CLEAR CART
                if order.user:
                    Cart.objects.filter(user=order.user).delete()

        except Order.DoesNotExist:
            return HttpResponse(status=404)

    return JsonResponse({"status": "ok"})
