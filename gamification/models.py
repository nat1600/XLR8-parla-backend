# gamification/models.py

from django.db import models
from django.conf import settings

class UserAchievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('streak_7', '7 días consecutivos'),
        ('streak_30', '30 días consecutivos'),
        ('streak_100', '100 días consecutivos'),
        ('phrases_50', '50 frases guardadas'),
        ('phrases_100', '100 frases guardadas'),
        ('phrases_500', '500 frases guardadas'),
        ('perfect_10', '10 sesiones perfectas'),
        ('speed_demon', 'Contrarreloj < 2 min'),
        ('polyglot', '3+ idiomas'), ## TODO: i know we are not integrate another languaje, but maybe we could leave this one
        ('points_1000', '1,000 puntos'),
        ('points_5000', '5,000 puntos'),
        ('points_10000', '10,000 puntos'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    achieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ['user', 'achievement_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_achievement_type_display()}"


class DailyStatistic(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_statistics')
    date = models.DateField()
    phrases_practiced = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    practice_minutes = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    streak_maintained = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'daily_statistics'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    