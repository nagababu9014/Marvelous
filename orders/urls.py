from django.urls import path
from .views import (
    CreateOrderAPIView,
    OrderByTokenAPIView,
    MyOrdersAPIView,
    SaveAddressAPIView,
    AddressListAPIView,
    SelectAddressAPIView,
    OrderTrackingAPIView,
)

urlpatterns = [
    path("create/", CreateOrderAPIView.as_view(), name="order-create"),
    path("", MyOrdersAPIView.as_view(), name="my-orders"),
    path("by-token/<uuid:token>/", OrderByTokenAPIView.as_view(), name="order-by-token"),

    path("save-address/", SaveAddressAPIView.as_view(), name="save-address"),
    path("addresses/", AddressListAPIView.as_view(), name="address-list"),
    path("select-address/", SelectAddressAPIView.as_view(), name="select-address"),
    path("track/<int:order_id>/", OrderTrackingAPIView.as_view()),
]
