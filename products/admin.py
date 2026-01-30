from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, SubCategory, Product

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')   # ✅ shows ID

@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'category')  # ✅ shows ID

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'category', 'subcategory', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'subcategory', 'is_active')
    ordering = ('order',)
