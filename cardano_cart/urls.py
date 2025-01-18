from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cardano_cart import views  # Replace with the actual app name
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),  # Root URL
    # Add other URLs here
    path('api/v1/users/', include('users.urls')),  # Include the users app's URLs
    path('api/v1/products/', include('products.urls')), # Include the products app)
    path('api/v1/orders/', include('orders.urls')), # Include the orders app
    #path('api/v1/cart/', include('cart.urls')), # Include the cart app
    path('api/v1/', include('reviews.urls')),
    path('api/v1/payments/', include("payments.urls")),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name="schema"),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name="schema"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

