from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password, make_password
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class RegisterView(APIView):
    @extend_schema(
        operation_id="register",
        request=RegisterSerializer,
        responses={201: UserProfileSerializer, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            full_user_data = UserProfileSerializer(user, context={'request': request}).data
            return Response({
                "message": "Account created successfully",
                "user": full_user_data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        operation_id="login",
        request=LoginSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is not None:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                raise AuthenticationFailed("Invalid email or password.")
        return Response({
            "error": "Invalid input",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,  # No complex request schema
        parameters=[
            OpenApiParameter(
                name='id',
                description="ID of the user",
                required=True,
                type=OpenApiTypes.INT
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(
        request=UserProfileSerializer,  # Schema for request data
        parameters=[
            OpenApiParameter(
                name='id',
                description="ID of the user",
                required=True,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name='current_password',
                description="Current password of the user (optional)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='new_password',
                description="New password for the user (optional)",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ]
    )
    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the requesting user is updating their own profile or has admin permissions
        if request.user.id != user.id and not request.user.is_superuser:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # Check for current password in the request
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)

        if current_password and new_password:
            # Verify the current password
            if not check_password(current_password,user.password):
                return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            # If it matches, set the new password
            user.password = make_password(new_password)  # Hash the new password
            user.save()  # Save the updated user instance

        # Update other fields if they are provided in the request
        serializer = UserProfileSerializer(user, data=request.data, partial=True, context={'request': request})  # `partial=True` for partial updates
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Invalid input",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the requesting user is deleting their own profile or has admin permissions
        if request.user.id != user.id and not request.user.is_superuser:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    

class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserProfileSerializer(many=True))
    def get(self, request, *args, **kwargs):
        users = CustomUser.objects.all()
        serializer = UserProfileSerializer(users, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserProfileSerializer)
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
