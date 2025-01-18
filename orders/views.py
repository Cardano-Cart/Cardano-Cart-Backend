from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Order
from .serializers import OrderSerializer
from products.models import Product


class OrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OrderSerializer)
    def post(self, request):
        # Retrieve product ID from the request
        product_id = request.data.get('product')
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the product the user wants to order
        product = get_object_or_404(Product, id=product_id)

        # Prepare the data for the order
        order_data = {
            'product': product_id,  # The single product for this order
            'shipping_address': request.data.get('shipping_address'),
            'tracking_number': request.data.get('tracking_number', ''),
        }

        # Pass the product and request context to the serializer
        serializer = self.get_serializer(data=order_data, context={'request': request})

        if serializer.is_valid():
            order = serializer.save()

            return Response({
                "message": "Order created successfully",
                "order": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="retrieve_orders",
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Optional order ID to retrieve a specific order",
            )
        ],
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, request, order_id=None):
        if request.user.role == 'admin':
            if order_id:
                # Get the order by ID
                order = get_object_or_404(Order, id=order_id)
                serializer = self.get_serializer(order, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Get all orders for admin
            orders = Order.objects.all()
            serializer = self.get_serializer(orders, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif order_id is not None:
            # Get the user's specific order
            order = get_object_or_404(Order, id=order_id, buyer=request.user)
            serializer = self.get_serializer(order, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Get all orders for the current user
        orders = Order.objects.filter(buyer=request.user)
        serializer = self.get_serializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, order_id=None):
        if order_id is not None:
            # Get the order and check ownership or admin permission
            order = get_object_or_404(Order, id=order_id, buyer=request.user)

            # Ensure the requesting user is deleting their own order or has admin permissions
            if request.user != order.buyer and not request.user.is_superuser:
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
            order.delete()
            return Response({
                "message": "Order deleted successfully."
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="update_order",
        request=OrderSerializer,
        responses={200: OrderSerializer, 400: OpenApiTypes.OBJECT},
    )
    def put(self, request, order_id=None):
        if order_id is not None:
            # Retrieve order by ID or return 404 if not found
            order = get_object_or_404(Order, id=order_id, buyer=request.user)

            # Ensure the requesting user is updating their own order or has admin permissions
            if request.user != order.buyer and not request.user.is_superuser:
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

            # Update the order
            serializer = OrderSerializer(order, data=request.data, context={'request': request}, partial=False)  # full update (PUT)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Order updated successfully",
                    "order": serializer.data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)
