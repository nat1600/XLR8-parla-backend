from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from gamification.services.streak_service import StreakService
from gamification.services.points_service import PointsService
from gamification.models import DailyStatistic, UserAchievement

User = get_user_model()


# Streak service tests
class TestStreakService(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user_streak",
            password="test123"
        )

    def test_initial_streak(self):
        result = StreakService.register_activity(self.user)
        self.user.refresh_from_db()
        self.assertEqual(result["streak"], 1)

    def test_streak_increment(self):
        self.user.current_streak = 1
        self.user.last_practice_date = date.today() - timedelta(days=1)
        self.user.save()

        result = StreakService.register_activity(self.user)
        self.assertEqual(result["streak"], 2)

    def test_streak_reset(self):
        self.user.current_streak = 10
        self.user.last_practice_date = date.today() - timedelta(days=3)
        self.user.save()

        result = StreakService.register_activity(self.user)
        self.assertEqual(result["streak"], 1)


# Points Service Tests
class TestPointsService(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user_points",
            password="test123"
        )

    def test_add_points(self):
        PointsService.add_points(self.user, 50)
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 50)

    def test_daily_stats_created(self):
        PointsService.add_points(self.user, 20)

        stat = DailyStatistic.objects.filter(user=self.user).first()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.points_earned, 20)


# Achievements Tests
class TestAchievements(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user_ach",
            password="test123"
        )

    def test_points_achievement(self):
        PointsService.add_points(self.user, 2000)
        self.assertTrue(
            UserAchievement.objects.filter(
                user=self.user,
                achievement_type="points_1000"
            ).exists()
        )

    def test_streak_achievement(self):
        self.user.current_streak = 7
        self.user.last_practice_date = date.today() - timedelta(days=1)
        self.user.save()

        StreakService.register_activity(self.user)

        self.assertTrue(
            UserAchievement.objects.filter(
                user=self.user,
                achievement_type="streak_7"
            ).exists()
        )


# Endpoint Tests 
class TestGamificationEndpoints(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user_api",
            password="test123"
        )
        self.client.login(username="user_api", password="test123")

    def test_get_streak(self):
        url = reverse("current-streak")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_points_endpoint(self):
        url = reverse("add-points")
        response = self.client.post(url, {"amount": 30})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_points"], 30)

    def test_achievements_endpoint(self):
        UserAchievement.objects.create(
            user=self.user,
            achievement_type="points_1000"
        )

        url = reverse("user-achievements")
        response = self.client.get(url)
        self.assertGreater(len(response.data), 0)

    def test_leaderboard_endpoint(self):
        url = reverse("leaderboard")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
