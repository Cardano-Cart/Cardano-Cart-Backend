from django.urls import path
from .views import CustomGoogleLoginView

urlpatterns = [
    path('google/', CustomGoogleLoginView.as_view(), name='google-login'),
]