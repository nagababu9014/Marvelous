from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView

# Create your views here.
from rest_framework.generics import ListAPIView
from .models import Category
from .serializers import CategorySerializer
from .models import SubCategory
from .serializers import SubCategorySerializer
from rest_framework.permissions import AllowAny
class CategoryListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryListAPIView(ListAPIView): 
    permission_classes = [AllowAny]

    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.request.query_params.get("category")
        if category_id:
            return SubCategory.objects.filter(category_id=category_id)
        return SubCategory.objects.all()


from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        category_id = self.request.query_params.get("category")
        subcategory_id = self.request.query_params.get("subcategory")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        return queryset
class ProductDetailAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product

class ProductSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.GET.get("q", "").strip()

        if not q:
            return Response([])

        products = Product.objects.filter(
            name__icontains=q
        )[:8]  # limit results like Amazon

        return Response([
            {
                "id": p.id,
                "name": p.name,
                "image": p.image.url if p.image else "",
                "price": p.price
            }
            for p in products
        ])
