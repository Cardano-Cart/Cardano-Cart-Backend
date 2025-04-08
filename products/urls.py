from django.urls import path
from .views import CategoryListCreateView, CategoryRetrieveUpdateDestroyView, ProductView, SubcategoryListCreateView, SubcategoryRetrieveUpdateDestroyView

urlpatterns = [
    path('', ProductView.as_view(), name='product-list-create'),
    path('<int:id>/', ProductView.as_view(), name='get-update-delete-product'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    
    # Subcategory URLs
    path('subcategories/', SubcategoryListCreateView.as_view(), name='subcategory-list-create'),
    path('subcategories/<int:pk>/', SubcategoryRetrieveUpdateDestroyView.as_view(), name='subcategory-detail'),
]