from django.urls import path
from .views import PaymentAPIView
from .stripe_views import CreateStripePaymentIntent
from .webhooks import stripe_webhook
urlpatterns = [
    path("", PaymentAPIView.as_view(), name="payment"),
    path("create-intent/", CreateStripePaymentIntent.as_view()),
    path("webhook/", stripe_webhook),
]
