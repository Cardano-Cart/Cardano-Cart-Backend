from rest_framework import serializers
from .models import Product, ProductImage, Category, Subcategory
from users.models import CustomUser

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    image_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    class Meta:
        model = ProductImage
        fields = ['image', 'image_url']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_id']


class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.SerializerMethodField()

    images = ProductImageSerializer(many=True, required=False, read_only=True)
    seller = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)
    subcategory = SubcategorySerializer(read_only=True)
    subcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(),
        source='subcategory',
        write_only=True
    )

    def get_category_name(self, obj):
        return obj.subcategory.category.name if obj.subcategory and obj.subcategory.category else None

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock','category_name', 'subcategory',
            'subcategory_id', 'sku', 'specifications', 'images',
            'seller', 'created_at', 'updated_at'
        ]

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
