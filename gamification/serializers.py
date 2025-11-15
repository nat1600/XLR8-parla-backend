from rest_framework import serializers
from .models import UserAchievement, DailyStatistic


class UserAchievementSerializer(serializers.ModelSerializer):
    """
    serializer achivementes user
    """
    achievement_name = serializers.CharField(
        source='get_achievement_type_display',
        read_only=True
    )
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = [
            'id',
            'user',
            'achievement_type',
            'achievement_name',
            'achieved_at',
        ]
        read_only_fields = ['id', 'achieved_at']


class DailyStatisticSerializer(serializers.ModelSerializer):
    """
    Serializer daily stadistics
    """
    user = serializers.StringRelatedField(read_only=True)
    accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyStatistic
        fields = [
            'id',
            'user',
            'date',
            'phrases_practiced',
            'correct_answers',
            'practice_minutes',
            'points_earned',
            'streak_maintained',
            'accuracy',
        ]
        read_only_fields = ['id']
    
    def get_accuracy(self, obj):
        """Calcular porcentaje de acierto"""
        if obj.phrases_practiced == 0:
            return 0
        return round((obj.correct_answers / obj.phrases_practiced) * 100, 2)


class WeeklyStatsSerializer(serializers.Serializer):
    """
    Serializer weekly stadistics added
    """
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    total_phrases = serializers.IntegerField()
    total_correct = serializers.IntegerField()
    total_minutes = serializers.IntegerField()
    total_points = serializers.IntegerField()
    days_practiced = serializers.IntegerField()
    average_accuracy = serializers.FloatField()


class MonthlyStatsSerializer(serializers.Serializer):
    """
    Serializer monthly stadistics
    """
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    total_phrases = serializers.IntegerField()
    total_points = serializers.IntegerField()
    days_active = serializers.IntegerField()
    best_streak = serializers.IntegerField()