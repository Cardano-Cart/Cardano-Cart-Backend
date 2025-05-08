from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'address', 'phone_number', 'wallet_id', 'avatar', 'avatar_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'wallet_id': {'write_only': True}
        }

    def create(self, validated_data):
        try:
            with transaction.atomic():
                avatar = validated_data.pop('avatar', None)
                password = validated_data.pop('password')

                user = CustomUser.objects.create(**validated_data)

                if avatar:
                    user.avatar = avatar

                user.set_password(password)
                user.save()
                return user

        except IntegrityError as e:
            raise serializers.ValidationError("A user with this email or username already exists.")
        except Exception as e:
            raise serializers.ValidationError(f"Error creating user: {str(e)}")

    
    def validate(self, data):
        required_fields = ['username', 'email', 'password']  # Adjust based on your actual required fields

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise serializers.ValidationError({
                'missing_fields': f"Missing required fields: {', '.join(missing_fields)}"
            })
        return data
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise serializers.ValidationError({
                'missing_fields': f"Missing required fields: {', '.join(missing_fields)}"
            })
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone_number', 'role', 'wallet_id', 'avatar', 'avatar_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'role']

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

