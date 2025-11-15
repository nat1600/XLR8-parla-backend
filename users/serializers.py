from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_picture',
            'total_points',
            'current_streak',
            'longest_streak',
            'last_practice_date',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'total_points',
            'current_streak',
            'longest_streak',
            'date_joined',
        ]


class UserStatsSerializer(serializers.ModelSerializer):
    """
    statistics per user
    """
    total_phrases = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'total_points',
            'current_streak',
            'longest_streak',
            'total_phrases',
            'total_sessions',
            'accuracy',
        ]
    
    def get_total_phrases(self, obj):
        """phrases saved"""
        return obj.phrases.count()
    
    def get_total_sessions(self, obj):
        """completed sessions"""
        return obj.practice_sessions.filter(completed=True).count()
    
    def get_accuracy(self, obj):
        """percentaje of successes"""
        sessions = obj.practice_sessions.filter(completed=True)
        if not sessions.exists():
            return 0
        
        total_correct = sum(s.correct_answers for s in sessions)
        total_answers = sum(s.correct_answers + s.incorrect_answers for s in sessions)
        
        if total_answers == 0:
            return 0
        
        return round((total_correct / total_answers) * 100, 2)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    new users
    """

    ## TODO: review if this is fine or if  it helps
    pass 