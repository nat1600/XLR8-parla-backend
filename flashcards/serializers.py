from rest_framework import serializers
from .models import FlashcardReview, PracticeSession, PracticeSessionDetail
from phrases.serializers import PhraseListSerializer
from phrases.models import Phrase


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardReview
        fields = "__all__"

class FlashcardReviewSerializer(serializers.ModelSerializer):
    phrase = serializers.PrimaryKeyRelatedField(
        queryset=Phrase.objects.all(),  
        required=True
    )
    accuracy = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardReview
        fields = [
            'id',
            'phrase',
            'repetitions',
            'interval',
            'ef',
            'next_review_date',
            'total_reviews',
            'correct_reviews',
            'accuracy',
            'last_reviewed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'next_review_date',
            'repetitions',
            'interval',
            'ef',
            'total_reviews',
            'correct_reviews',
        ]

    def get_accuracy(self, obj):
        if obj.total_reviews == 0:
            return 0
        return round((obj.correct_reviews / obj.total_reviews) * 100, 2)



class PracticeSessionDetailSerializer(serializers.ModelSerializer):
    """
    sesion details
    """
    phrase = PhraseListSerializer(read_only=True)
    
    class Meta:
        model = PracticeSessionDetail
        fields = [
            'id',
            'phrase',
            'was_correct',
            
            'response_time_seconds',
            'answered_at',
        ]


class PracticeSessionSerializer(serializers.ModelSerializer):
    """
    practice sessions
    """
    details = PracticeSessionDetailSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    accuracy = serializers.SerializerMethodField()
    session_type_display = serializers.CharField(
        source='get_session_type_display',
        read_only=True
    )
    
    class Meta:
        model = PracticeSession
        fields = [
            'id',
            'session_type',
            'session_type_display',
            'phrases_practiced',
            'correct_answers',
            'incorrect_answers',
            'points_earned',
            'duration_seconds',
            'completed',
            'accuracy',
            'started_at',
            'completed_at',
            'mode_data',
            'details',
            'user',
        ]
        read_only_fields = [
            'id',
            'user',
            'phrases_practiced',
            'correct_answers',
            'incorrect_answers',
            'points_earned',
            'duration_seconds',
            'started_at',
            'completed_at',
            'mode_data',
            'accuracy',
            'session_type_display',
        ]
    
    def get_accuracy(self, obj):
        """Calculate success percentage for the session."""
        total = obj.correct_answers + obj.incorrect_answers
        if total == 0:
            return 0
        return round((obj.correct_answers / total) * 100, 2)


class PracticeSessionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer when the user stats a practice session
    """
    class Meta:
        model = PracticeSession
        fields = ['session_type']


class ReviewAnswerSerializer(serializers.Serializer):
    """
    resgister
    """
    phrase_id = serializers.IntegerField()
    practice_session  = serializers.IntegerField()
    was_correct = serializers.BooleanField()
    response_time = serializers.IntegerField(required=False, allow_null=True)
    



class FlashcardSM2AnswerSerializer(serializers.Serializer):
    """
    Serializer para validar la calidad (0-5) de la respuesta del usuario.
    Este serializer NO crea ni actualiza flashcards,
    solo valida el input de la vista.
    """
    quality = serializers.IntegerField(min_value=0, max_value=5)

    def validate_quality(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError(
                "Quality must be between 0 and 5."
            )
        return value
