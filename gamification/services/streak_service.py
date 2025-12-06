# gamification/services/streak_service.py
from datetime import date, timedelta
from django.db import transaction
from gamification.models import DailyStatistic
from gamification.services.achievement_service import AchievementService


class StreakService:

    @staticmethod
    @transaction.atomic
    def register_activity(user):
        today = date.today()

        if user.last_practice_date is None:
            user.current_streak = 1
        else:
            delta = today - user.last_practice_date
            if delta == timedelta(days=1):
                user.current_streak = (user.current_streak or 0) + 1
            elif delta == timedelta(days=0):
                pass
            else:
                user.current_streak = 1

        user.last_practice_date = today

        if (user.longest_streak or 0) < user.current_streak:
            user.longest_streak = user.current_streak

        user.save(update_fields=["current_streak", "longest_streak", "last_practice_date"])

        # get or create daily stat
        daily, created = DailyStatistic.objects.get_or_create(
            user=user,
            date=today,
        )

        daily.streak_maintained = user.current_streak > 1
        daily.save(update_fields=["streak_maintained"])

        try:
            AchievementService.check_streak_achievements(user)
        except Exception:
            pass

        return {
            "streak": user.current_streak,
            "best_streak": user.longest_streak
        }
