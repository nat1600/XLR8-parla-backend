from rest_framework import serializers
from .models import FlashcardReview, PracticeSession, PracticeSessionDetail
from phrases.serializers import PhraseListSerializer


class FlashcardReviewSerializer(serializers.ModelSerializer):
    """
    per flashcards
    """
    phrase = PhraseListSerializer(read_only=True)
    accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = FlashcardReview
        fields = [
            'id',
            'phrase',
            'repetitions',
            'ease_factor',
            'interval_days',
            'next_review_date',
            'total_reviews',
            'correct_reviews',
            'accuracy',
            'last_reviewed_at',
        ]
    
    def get_accuracy(self, obj):
        """percentage succes """
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
            'score',
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
        ]
    
    def get_accuracy(self, obj):
        """sucess"""
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
    session_id = serializers.IntegerField()
    was_correct = serializers.BooleanField()
    response_time = serializers.IntegerField(required=False, allow_null=True)
    score = serializers.IntegerField(required=False, default=0)