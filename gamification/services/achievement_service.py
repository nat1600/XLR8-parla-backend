# gamification/services/achievement_service.py

from gamification.models import UserAchievement


class AchievementService:
    """
    this service is responsible for:
    - check conditions for points
    - check conditions for streaks
    - register newly unlocked achievements
    """

    # Register a new achievement
    @staticmethod
    def unlock(user, achievement_type):
        """
        Create an achievement for the user if not already unlocked.
        """
        achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement_type=achievement_type
        )
        return created

    # Achievement checks
    @staticmethod
    def check_points_achievements(user):
        """
        Check the user's total points
        and unlock achievements based on thresholds.
        """
        points = user.total_points or 0

        if points >= 10000:
            AchievementService.unlock(user, "points_10000")
        if points >= 5000:
            AchievementService.unlock(user, "points_5000")
        if points >= 1000:
            AchievementService.unlock(user, "points_1000")

    # Achievement based on streaks
    @staticmethod
    def check_streak_achievements(user):
        """
        Check the user's current streak
        """
        streak = user.current_streak or 0

        if streak >= 100:
            AchievementService.unlock(user, "streak_100")
        if streak >= 30:
            AchievementService.unlock(user, "streak_30")
        if streak >= 7:
            AchievementService.unlock(user, "streak_7")
