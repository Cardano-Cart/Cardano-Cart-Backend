from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from products.models import Product
from orders.models import Order
from payments.backends import verify_payment
from payments.serializers import PaymentVerificationSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class GetPaymentAddressView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="get_payment_address",
        description="Retrieve the seller's payment address for a given product ID.",
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        })
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)  # Get the order by ID
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the seller's wallet address from the order's product
            seller_address = product.seller.wallet_id

            # Return the generated address
            if not seller_address:
                return Response({
                    "message": "Seller's payment address not found",
                }, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "message": "Payment address obtained successfully",
                "payment_address": str(seller_address)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="verify_payment",
        description="Verify a payment for a given order ID.",
        request=PaymentVerificationSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        })
    def post(self, request, order_id):
        # Retrieve the order using the order_id from the URL
        try:
            order = Order.objects.get(id=order_id)  # Get the order by ID
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentVerificationSerializer(data=request.data, context={'order': order})
        if serializer.is_valid():
            transaction_id = serializer.validated_data['transaction_id']
            # Use the order to get seller_address and expected_amount
            seller_address = order.product.seller.wallet_id
            expected_amount = order.total_amount

            # Call the verify_payment function
            is_verified = verify_payment(transaction_id, seller_address, expected_amount)

            if is_verified:
                order.status = 'paid'
                order.save()
                return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    
