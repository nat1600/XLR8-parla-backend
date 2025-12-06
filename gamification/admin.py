# 9. gamification/admin.py

from django.contrib import admin
from .models import UserAchievement, DailyStatistic


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement_type", "achieved_at")
    list_filter = ("achievement_type", "achieved_at")
    search_fields = ("user__username",)


@admin.register(DailyStatistic)
class DailyStatisticAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date",
        "phrases_practiced",
        "correct_answers",
        "practice_minutes",
        "points_earned",
        "streak_maintained",
    )
    list_filter = ("date", "streak_maintained")
    search_fields = ("user__username",)
