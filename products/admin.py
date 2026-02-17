from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from .models import Category, SubCategory, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')   # ✅ shows ID

@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'category')  # ✅ shows ID

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'is_primary')


# 🔥 CHANGE HERE
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'category', 'subcategory', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'subcategory', 'is_active')
    ordering = ('order',)
    inlines = [ProductImageInline]

    fieldsets = (
        ("General", {
            "fields": (
                "category",
                "subcategory",
                "name",
                "price",
                "description",
                "stock",
                "order",
                "is_active",
            )
        }),
    )
