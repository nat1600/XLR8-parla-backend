# flashcards/views.py

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import FlashcardReview, PracticeSession, PracticeSessionDetail
from .serializers import (
    FlashcardReviewSerializer,
    FlashcardSM2AnswerSerializer

)

from phrases.models import Phrase
from flashcards.services.sm2 import sm2 


class FlashcardsDueView(APIView):
    """
         Retrieve flashcards that are due for review based on spaced repetition scheduling.sm2.

        ENDPOINT:
        GET /api/flashcards/due/

         FILTERING:
        - Automatically filters by current authenticated user
        - Only returns cards where next_review_date <= current time
        - Limited to 20 items per request (configurable)
    
    EXAMPLE USAGE:
        GET /api/flashcards/due/
        → Returns cards scheduled for review today or earlier
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        

        now = timezone.now()

        reviews = FlashcardReview.objects.filter(
            user=request.user,
            next_review_date__lte=now
        ).order_by("next_review_date")[:20] 

        serializer = FlashcardReviewSerializer(reviews,many=True)
        return Response(serializer.data)
    


class FlashcardAnswerView(APIView):

    """
    Process user's answer to a flashcard and update spaced repetition schedule.

    ENDPOINT:
        POST /api/flashcards/{phrase_id}/answer/

    BODY:
        { "quality": int }   (0–5)
        FRONT: This is like the bottoms that are marked like good or bad, i dont know how work this lol

    EXAMPLE:
        POST /api/flashcards/123/answer/
        BODY: {"quality": 5}
        RESPONSE: {"interval_days": 10, "ef": 2.6, ...}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, phrase_id):
        serializer = FlashcardSM2AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quality = serializer.validated_data["quality"]

        # Obtain or create the SM-2 record
        review, _ = FlashcardReview.objects.get_or_create(
            user=request.user,
            phrase_id=phrase_id
        )

        # Apply SM-2 algorithm
        sm2(review, quality)

        return Response({
            "message": "Flashcard updated successfully.",
            "interval_days": review.interval,
            "ef": review.ef,
            "repetitions": review.repetitions,
            "next_review": review.next_review_date
        })

        
class FlashListCreateView(generics.ListCreateAPIView):

    """
    List all flashcards for authenticated user and create new flashcards.
    ENDPOINTS:
        GET  /api/flashcards/     - List all user's flashcards
        POST /api/flashcards/     - Create a new flashcard
    """

    serializer_class = FlashcardReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FlashcardReview.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FlashDetailView(generics.RetrieveUpdateDestroyAPIView):

    """
    CRUD Flascards.
    Retrieve, update, or delete a specific flashcard.


    ENDPOINTS:
        GET    /api/flashcards/{id}/  - Retrieve flashcard details
        PUT    /api/flashcards/{id}/  - Update entire flashcard
        PATCH  /api/flashcards/{id}/  - Partially update flashcard
        DELETE /api/flashcards/{id}/  - Delete flashcard

    EXAMPLE:
        GET /api/flashcards/5/ → Returns details of flashcard 5 (if owned by user)
        DELETE /api/flashcards/5/ → Deletes flashcard 5 (if owned by user)

    """
    serializer_class = FlashcardReviewSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return FlashcardReview.objects.filter(user = self.request.user)


