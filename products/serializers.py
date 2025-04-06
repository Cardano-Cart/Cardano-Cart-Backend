from rest_framework import serializers
from .models import Product, ProductImage
from users.models import CustomUser

class ProductImageSerializer(serializers.ModelSerializer):
    # Directly return the URL of the image field
    image = serializers.ImageField(use_url=True)  # This line can remain if you want to return the image file
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        # Construct the full URL including host
        request = self.context.get('request')
        if request is not None:
            full_url = request.build_absolute_uri(obj.image.url)
            return full_url
        return None

    class Meta:
        model = ProductImage
        fields = ['image', 'image_url']  # Include the image field directly

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    seller = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'subcategory', 'sku', 'specifications', 'images', 'seller', 'created_at']

    def validate(self, data):
        required_fields = ['name', 'price', 'description']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise serializers.ValidationError({
                'missing_fields': f"Missing required fields: {', '.join(missing_fields)}"
            })
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        images_data = self.context['request'].FILES.getlist('images')
        product = Product.objects.create(seller=user, **validated_data)
        for image in images_data:
            image_instance = ProductImage.objects.create(image=image)
            product.images.add(image_instance)
        return product

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data:
            instance.images.clear()
            for image in images_data:
                image_instance = ProductImage.objects.create(image=image)
                instance.images.add(image_instance)
        return instance
