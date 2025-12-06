# gamification/services/points_service.py

from datetime import date
from django.db import transaction
from gamification.models import DailyStatistic
from gamification.services.achievement_service import AchievementService


class PointsService:
    """
    Manages user points addition and related achievements:
    - AddS points to the user
    - Updates DailyStatistic with earned points
    - Checks and unlocks point-based achievements
    """

    @staticmethod
    @transaction.atomic
    def add_points(user, amount):
        """
        - Add points to the user and update daily statistics.
        """
        # Validación mínima
        if amount <= 0:
            return user.total_points

        user.total_points = (user.total_points or 0) + int(amount)
        user.save(update_fields=["total_points"])

        today = date.today()
        daily, _ = DailyStatistic.objects.get_or_create(
            user=user,
            date=today,
        )

        daily.points_earned = (daily.points_earned or 0) + int(amount)
        daily.save(update_fields=["points_earned"])

        try:
            AchievementService.check_points_achievements(user)
        except Exception:
            pass

        return user.total_points
