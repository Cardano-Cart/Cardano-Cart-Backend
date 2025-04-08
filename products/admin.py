from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = Product.images.through  # Use the through model for the many-to-many relationship
    extra = 1  # Allows you to add one image by default

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    list_display = ('name', 'seller', 'price', 'stock', 'get_category', 'created_at')
    search_fields = ('name', 'subcategory__name', 'subcategory__category__name')

    def get_category(self, obj):
        return obj.subcategory.category.name if obj.subcategory and obj.subcategory.category else None
    get_category.short_description = 'Category'


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image',)  # Display the image field in the admin list view

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)