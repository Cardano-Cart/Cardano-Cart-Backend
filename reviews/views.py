# views.py

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from .models import Review, Product
from .serializers import ReviewSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class ReviewView(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    
    @extend_schema(
        operation_id="add_review",
        request=ReviewSerializer,
        responses={201: ReviewSerializer, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request, product_id):
    # Get the product from the URL
        product = get_object_or_404(Product, id=product_id)
        
        # Pass the product to the serializer via context
        serializer = ReviewSerializer(data=request.data, context={'request': request, 'product': product})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Review added successfully",
                "review": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @extend_schema(
    operation_id="UpdateReview",
    description="Update an existing review for a specific product. Only the owner of the review or an admin can perform this action.",
    request=ReviewSerializer,
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID of the product to which the review belongs.",
        ),
        OpenApiParameter(
            name="review_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID of the review to be updated.",
        ),
    ])
    def put(self, request, product_id, review_id):
        try:
            # Fetch the review that needs to be updated
            review = Review.objects.get(id=review_id, product=product_id, user=request.user)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensuring the requesting user is updating their own review(s) or has admin permissions
        if request.user != review.user and not request.user.is_superuser:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        

        # Validate and update the review
        serializer = ReviewSerializer(review, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Review updated successfully",
                "review": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, product_id, review_id):
        try:
            # Fetch the review that needs to be deleted
            review = Review.objects.get(id=review_id, product_id=product_id, user=request.user)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensuring the requesting user is deleting their own review(s) or has admin permissions
        if request.user != review.user and not request.user.is_superuser:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Delete the review
        review.delete()
        return Response({"message": "Review deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

    @extend_schema(
    operation_id="GetReviews",
    description=(
        "Retrieve reviews for a specific product. "
        "If `review_id` is provided, fetch the specific review. "
        "Otherwise, fetch all reviews for the product."
    ),
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID of the product for which reviews are being retrieved.",
        ),
        OpenApiParameter(
            name="review_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=False,
            description="ID of the specific review to retrieve. Optional.",
        ),
    ])
    def get(self, request, product_id, review_id=None):

        if not review_id:
            # Fetch all reviews for the given product
            try:
                reviews = Review.objects.filter(product_id=product_id)
            
                # Serialize the reviews
                serializer = ReviewSerializer(reviews, many=True)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Fetch the review by ID and product ID
            review = Review.objects.get(id=review_id, product_id=product_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the review data
        serializer = ReviewSerializer(review)
        
        # Prepare the response data
        review_data = serializer.data
        review_data['created_at'] = review.created_at.isoformat()

        return Response(review_data, status=status.HTTP_200_OK)
    





    