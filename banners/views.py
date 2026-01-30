from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from .models import Banner
from .serializers import BannerSerializer
from rest_framework.permissions import AllowAny


class BannerListAPIView(ListAPIView):
    permission_classes = [AllowAny]

    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
