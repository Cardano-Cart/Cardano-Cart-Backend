from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


User = get_user_model()

class CustomGoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('credential')
        if not token:
            return Response({'error': 'No token provided'}, status=400)

        try:
            # Verify the token using Google's public keys
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            user, created = User.objects.get_or_create(email=email, defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': email.split('@')[0]
            })

            if created:
                user.role = 'customer'
                user.email_verified = True
                user.save()
            
            elif user:
                if user.is_deleted:
                    return Response({'message': 'User account has been deleted.'}, status=status.HTTP_403_FORBIDDEN)
                elif not user.is_active:
                    return Response({'message': 'User account is inactive.'}, status=status.HTTP_403_FORBIDDEN)



            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })

        except ValueError:
            return Response({'error': 'Invalid token'}, status=400)