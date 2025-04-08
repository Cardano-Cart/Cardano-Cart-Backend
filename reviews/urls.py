# urls.py

from django.urls import path
from .views import ReviewView

urlpatterns = [
    path('reviews/<int:product_id>/', ReviewView.as_view(), name='add-review'),
    path('<int:product_id>/reviews/<int:review_id>/', ReviewView.as_view(), name='particular_review'),
    path('<int:product_id>/reviews/', ReviewView.as_view(), name="all_product_reviews")
]
