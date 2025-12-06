# flashcards/views.py

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

from .models import FlashcardReview, PracticeSession, PracticeSessionDetail
from .serializers import (
    FlashcardReviewSerializer,
    FlashcardSM2AnswerSerializer,
    PracticeSessionCreateSerializer,
    PracticeSessionSerializer,
    PracticeSessionDetailSerializer

)

from phrases.models import Phrase
from flashcards.services.sm2 import sm2 
import random

from .helpers import (
    choose_phrases_for_user,
    award_points_for_answer
)

# ========================
# FLASHCARDS BASE
# ========================
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


# ========================
# PRACTICE SESSION BASE
# ========================================================0

class StartPracticeSessionView(APIView):
    """
    create a new practice session
    ENDPOINT:
        POST /api/practice-sessions/
    BODY: {"session_type": "timed|matching|quiz"}


    EXAMPLE: 
        POST /api/practice-sessions/
        {
        "session_type":"quiz"
        }

    """

    permission_classes = [IsAuthenticated]


    def post(self, request):
          
            user = request.user
            session_type = request.data.get("session_type")

            if session_type not in ["flashcard", "timed", "matching", "quiz"]:
                return Response({"error": "not valid cause is not in session__tyoe"}, status=400)

            session = PracticeSession.objects.create(
                user=user,
                session_type=session_type,
                started_at=timezone.now(),
                completed=False
            )

            return Response(PracticeSessionSerializer(session).data, status=201)
            


class AddPracticeDetailView(APIView):

    """
    Register an answer.
    Records an individual practice attempt.
      Each call adds one practice detail and updates session statistics in real-time

    ENDPOINT:
        POST /api/practice-sessions/{session_id}/details/

    EXAMPLE:
        POST /api/practice-sessions/123/details/
        Content-Type: application/json
        
        {
            "phrase_id": 456,
            "was_correct": true,
            "response_time_seconds": 2.5
        }
    
    """

    permission_classes = [IsAuthenticated]
    def post(self, request, session_id):
        try:
            practice_session  = PracticeSession.objects.get(id=session_id, user=request.user)
        except PracticeSession.DoesNotExist:
            return Response({"error": "session not founf"}, status=404)

        phrase_id = request.data.get("phrase_id")
        was_correct = request.data.get("was_correct")
        response_time = request.data.get("response_time_seconds", 0)

        try:
            phrase = Phrase.objects.get(id=phrase_id)
        except Phrase.DoesNotExist:
            return Response({"error": "Phrase not found"}, status=404)

        detail = PracticeSessionDetail.objects.create(
            practice_session =practice_session ,
            phrase=phrase,
            was_correct=was_correct,
            response_time_seconds=response_time,
            answered_at=timezone.now()
        )

        # stadistics
        if was_correct:
            practice_session.correct_answers += 1
            practice_session.points_earned += 10
        else:
            practice_session.incorrect_answers += 1

        practice_session.phrases_practiced += 1
        practice_session.save()

        return Response(PracticeSessionDetailSerializer(detail).data, status=201)
    


    


class PracticeSessionListView(generics.ListAPIView):
    """
    Lisrs user´s practice sessions

    Retrieve all practice sessions for the authenticated user
    ordered by most recent first.

    ENDPOINT:
        GET /api/practice-sessions/
    EXAMPLE:
        GET /api/practice-sessions/
        
    """
    serializer_class = PracticeSessionCreateSerializer

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).order_by("-started_at")
    

class PracticeSessionDetailView(generics.RetrieveAPIView):

    """
    Get detailed information about a specific practice session,
    including all individual practice details (answers).

     ENDPOINT:
        GET /api/practice-sessions/{session_id}/


    """
    serializer_class = PracticeSessionSerializer
    lookup_field = "id"

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user)
    
class CompletePracticeSessionView(APIView):

    """"
    Mark an active practice session as completed and calculate its duration.
    ENDPOINT:
        POST /api/practice-sessions/{session_id}/complete/

        EXAMPLE:
        POST /api/practice-sessions/123/complete/
        Content-Type: application/json
        
        {}
    """
    def post(self, request, session_id):
        try:
            session = PracticeSession.objects.get(id=session_id, user=request.user)
        except PracticeSession.DoesNotExist:
            return Response({"error": "session not found"}, status=404)

        if session.completed:
            return Response({"error": "The session is finished"}, status=400)

        session.completed = True
        session.completed_at = timezone.now()
        session.duration_seconds = (session.completed_at - session.started_at).seconds
        session.save()

        return Response(PracticeSessionSerializer(session).data)


        
#//////////
#MATCH 
#------------------------

class MatchingStartView(APIView):
    """

    Start a new matching game session

    ENDPOINT:
        POST /api/flashcards/matching/start/

    EXAMPLE REQUEST:
        POST /api/flashcards/matching/start/
        
        {
            "pairs": whatever fronts wants :), it mustt be an integer, prefereably between 4-5
        }

    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pairs = int(request.data.get('pairs', 8))
        phrases = choose_phrases_for_user(request.user, pairs)

        # build pairs      : left = original_text , right = translated_text
        left = [{"id": p.id, "text": p.original_text} for p in phrases]
        right = [{"id": p.id, "text": p.translated_text} for p in phrases]

  
        random.shuffle(right)

        session = PracticeSession.objects.create(
            user=request.user,
            session_type="matching",
            mode_data={"pairs": [p.id for p in phrases], "right_order": [r["id"] for r in right]},
            started_at=timezone.now(),
            completed=False
        )

        return Response({
            "session": PracticeSessionSerializer(session).data,
            "left": left,
            "right": right
        }, status=status.HTTP_201_CREATED)
    


    
class MatchingCheckView(APIView):
    """
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        matches = request.data.get("matches", [])

        try:
            session = PracticeSession.objects.get(id=session_id, user=request.user)
        except PracticeSession.DoesNotExist:
            return Response({"error": "Sesión no encontrada"}, status=404)

        results = []
        correct_count = 0

        for m in matches:
            left_id = m.get("left_id")
            right_id = m.get("right_id")
            try:
                left_phrase = Phrase.objects.get(id=left_id)
                right_phrase = Phrase.objects.get(id=right_id)
            except Phrase.DoesNotExist:
                results.append({"left_id": left_id, "right_id": right_id, "correct": False, "error": "phrase not found"})
                continue

            is_correct = (left_phrase.id == right_phrase.id)
            results.append({"left_id": left_id, "right_id": right_id, "correct": is_correct})
            if is_correct:
                correct_count += 1

            # log detail
            PracticeSessionDetail.objects.create(
                practice_session=session,
                phrase=left_phrase,
                was_correct=is_correct,
                response_time_seconds=None
            )

            if is_correct:
                session.correct_answers += 1
            else:
                session.incorrect_answers += 1
            session.phrases_practiced += 1
            award_points_for_answer(session, is_correct, base=8)

        session.save()

        return Response({
            "results": results,
            "summary": PracticeSessionSerializer(session).data
        })

        




        