from django.urls import path
from .views import CategoryListAPIView, SubCategoryListAPIView, ProductListAPIView, ProductDetailAPIView, ProductSearchAPIView

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view()),
    path("subcategories/", SubCategoryListAPIView.as_view()),
    path("products/", ProductListAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),  # ✅ ADD THIS
    path("products/search/", ProductSearchAPIView.as_view()),  # ✅ FIX


]
