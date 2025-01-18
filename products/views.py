from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ProductSerializer
from .models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="add_product",
        request=ProductSerializer,
        responses={201: ProductSerializer, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Product added successfully",
                "product": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            {
                'name': 'id',
                'in': 'path',
                'required': False,
                'description': 'ID of the product to retrieve. If not provided, all products are retrieved.',
                'schema': {'type': 'integer'}
            }
        ],
        responses={
            200: ProductSerializer(many=True),
            404: {"description": "Product not found."}
        },
        description="Retrieve a specific product by its ID or retrieve all products if no ID is provided."
    )
    def get(self, request, id=None):
        if id is not None:
            # Retrieve product by ID or return 404 if not found
            product = get_object_or_404(Product, id=id)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Retrieve all products
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(
        parameters=[
            {
                'name': 'id',
                'in': 'path',
                'required': True,
                'description': 'ID of the product to update.',
                'schema': {'type': 'integer'}
            }
        ],
        request=ProductSerializer)
    def put(self, request, id=None):
        
        if id is not None:
            # Retrieve product by ID or return 404 if not found
            product_id = id
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
            
            product = get_object_or_404(Product, id=id)
            if request.user != product.seller and not request.user.is_superuser:
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = ProductSerializer(product, data=request.data, context={'request': request}, partial=False)  # full update (PUT)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Product updated successfully",
                    "product": serializer.data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, id=None):
        if id is not None:
            # Retrieve product by ID or return 404 if not found
            product_id = id
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
            product = get_object_or_404(Product, id=id)

            if request.user != product.seller and not request.user.is_superuser:
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
            product.delete()
            return Response({
                "message": "Product deleted successfully."
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

