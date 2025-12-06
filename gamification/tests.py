from django.test import TestCase
from django.contrib.auth import get_user_model
from gamification.models import UserStreak, DailyStatistic, UserAchievement
from datetime import date, timedelta


class UserStreakTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="123456"
        )

    def test_streak_initially_zero(self):
        streak = UserStreak.objects.create(user=self.user)
        self.assertEqual(streak.streak_count, 0)
        self.assertEqual(streak.best_streak, 0)
        self.assertIsNone(streak.last_activity)

    def test_streak_increment(self):
        streak = UserStreak.objects.create(user=self.user)
        streak.last_activity = date.today() - timedelta(days=1)
        streak.streak_count = 3
        streak.save()

        # Simulate today activity
        today = date.today()
        streak.last_activity = today
        streak.streak_count += 1
        streak.best_streak = max(streak.best_streak, streak.streak_count)
        streak.save()

        self.assertEqual(streak.streak_count, 4)
        self.assertEqual(streak.best_streak, 4)
        self.assertEqual(streak.last_activity, today)


class DailyStatisticTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="daily@example.com",
            password="123456"
        )

    def test_daily_statistic_creation(self):
        stat = DailyStatistic.objects.create(
            user=self.user,
            date=date.today(),
            phrases_practiced=10,
            correct_answers=8,
            practice_minutes=5,
            points_earned=20,
            streak_maintained=True,
        )

        self.assertEqual(stat.phrases_practiced, 10)
        self.assertEqual(stat.correct_answers, 8)
        self.assertEqual(stat.points_earned, 20)
        self.assertTrue(stat.streak_maintained)


class UserAchievementTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="achiever@example.com",
            password="123456"
        )

    def test_achievement_assignment(self):
        achievement = UserAchievement.objects.create(
            user=self.user,
            achievement_type="streak_7"
        )

        self.assertEqual(achievement.user, self.user)
        self.assertEqual(achievement.achievement_type, "streak_7")
