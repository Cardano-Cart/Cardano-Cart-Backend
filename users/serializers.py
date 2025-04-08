from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'address', 'phone_number', 'wallet_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'wallet_id': {'write_only': True}
        }

    def create(self, validated_data):
        try:
            # Start a transaction to ensure atomicity
            with transaction.atomic():
                user = CustomUser.objects.create(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', ''),
                    address=validated_data.get('address', ''),
                    phone_number=validated_data.get('phone_number', ''),
                )
                print("User created:", user)  # Print statement before saving
                user.set_password(validated_data['password'])
                user.save()  # Save the user after password hashing
                print("User saved:", user)  # Print statement after saving
                return user

        except IntegrityError as e:
            print("IntegrityError:", e)  # Log integrity error
            raise serializers.ValidationError("A user with this email or username already exists.")
        
        except Exception as e:
            print("Error:", e)  # Log other errors
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
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

