# gamification/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from gamification.models import UserAchievement, DailyStatistic
from gamification.services.points_service import PointsService
from gamification.services.streak_service import StreakService
from gamification.services.achievement_service import AchievementService

User = get_user_model()


# ========================
# SERVICE TESTS
# ========================

class PointsServiceTestCase(TestCase):
    """Test PointsService functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.user.total_points = 0
        self.user.save()
    
    def test_add_points_updates_user_total(self):
        """Test that adding points updates user.total_points"""
        PointsService.add_points(self.user, 100)
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 100)
    
    def test_add_points_updates_daily_statistics(self):
        """Test that adding points creates/updates daily statistics"""
        PointsService.add_points(self.user, 50)
        
        daily_stat = DailyStatistic.objects.get(
            user=self.user,
            date=date.today()
        )
        self.assertEqual(daily_stat.points_earned, 50)
    
    def test_add_points_multiple_times_accumulates(self):
        """Test that multiple point additions accumulate correctly"""
        PointsService.add_points(self.user, 100)
        PointsService.add_points(self.user, 50)
        PointsService.add_points(self.user, 25)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 175)
    
    def test_add_zero_points_does_nothing(self):
        """Test that adding 0 or negative points is ignored"""
        initial_points = self.user.total_points
        PointsService.add_points(self.user, 0)
        PointsService.add_points(self.user, -10)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, initial_points)
    
    def test_points_unlock_achievements(self):
        """Test that reaching point thresholds unlocks achievements"""
        PointsService.add_points(self.user, 1000)
        
        achievement = UserAchievement.objects.filter(
            user=self.user,
            achievement_type='points_1000'
        ).exists()
        self.assertTrue(achievement)


class StreakServiceTestCase(TestCase):
    """Test StreakService functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_first_activity_sets_streak_to_one(self):
        """Test that first activity sets streak to 1"""
        result = StreakService.register_activity(self.user)
        
        self.assertEqual(result['streak'], 1)
        self.assertEqual(result['best_streak'], 1)
    
    def test_same_day_activity_maintains_streak(self):
        """Test that multiple activities on same day don't increase streak"""
        StreakService.register_activity(self.user)
        result = StreakService.register_activity(self.user)
        
        self.assertEqual(result['streak'], 1)
    
    def test_consecutive_day_increases_streak(self):
        """Test that activity on consecutive days increases streak"""
        # Day 1
        StreakService.register_activity(self.user)
        
        # Simulate next day
        self.user.last_practice_date = date.today() - timedelta(days=1)
        self.user.save()
        
        # Day 2
        result = StreakService.register_activity(self.user)
        
        self.assertEqual(result['streak'], 2)
        self.assertEqual(result['best_streak'], 2)
    
    def test_gap_in_days_resets_streak(self):
        """Test that missing a day resets streak to 1"""
        # Day 1
        StreakService.register_activity(self.user)
        
        # Simulate 3 days later (gap)
        self.user.last_practice_date = date.today() - timedelta(days=3)
        self.user.current_streak = 5
        self.user.longest_streak = 5
        self.user.save()
        
        # Activity after gap
        result = StreakService.register_activity(self.user)
        
        self.assertEqual(result['streak'], 1)
        self.assertEqual(result['best_streak'], 5)  # best_streak preserved
    
    def test_longest_streak_updates_correctly(self):
        """Test that longest_streak updates when current exceeds it"""
        self.user.current_streak = 10
        self.user.longest_streak = 8
        self.user.last_practice_date = date.today() - timedelta(days=1)
        self.user.save()
        
        result = StreakService.register_activity(self.user)
        
        self.assertEqual(result['streak'], 11)
        self.assertEqual(result['best_streak'], 11)
    
    def test_streak_unlocks_achievements(self):
        """Test that reaching streak milestones unlocks achievements"""
        self.user.current_streak = 6
        self.user.last_practice_date = date.today() - timedelta(days=1)
        self.user.save()
        
        StreakService.register_activity(self.user)
        
        achievement = UserAchievement.objects.filter(
            user=self.user,
            achievement_type='streak_7'
        ).exists()
        self.assertTrue(achievement)


class AchievementServiceTestCase(TestCase):
    """Test AchievementService functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_unlock_creates_new_achievement(self):
        """Test that unlock creates a new achievement"""
        created = AchievementService.unlock(self.user, 'points_1000')
        
        self.assertTrue(created)
        achievement = UserAchievement.objects.get(
            user=self.user,
            achievement_type='points_1000'
        )
        self.assertIsNotNone(achievement)
    
    def test_unlock_same_achievement_twice_does_not_duplicate(self):
        """Test that unlocking same achievement twice doesn't create duplicate"""
        AchievementService.unlock(self.user, 'points_1000')
        created = AchievementService.unlock(self.user, 'points_1000')
        
        self.assertFalse(created)
        count = UserAchievement.objects.filter(
            user=self.user,
            achievement_type='points_1000'
        ).count()
        self.assertEqual(count, 1)
    
    def test_check_points_achievements_unlocks_all_eligible(self):
        """Test that check_points_achievements unlocks all eligible achievements"""
        self.user.total_points = 5500
        self.user.save()
        
        AchievementService.check_points_achievements(self.user)
        
        achievements = UserAchievement.objects.filter(user=self.user)
        achievement_types = [a.achievement_type for a in achievements]
        
        self.assertIn('points_1000', achievement_types)
        self.assertIn('points_5000', achievement_types)
        self.assertNotIn('points_10000', achievement_types)
    
    def test_check_streak_achievements_unlocks_correctly(self):
        """Test that check_streak_achievements unlocks based on current streak"""
        self.user.current_streak = 30
        self.user.save()
        
        AchievementService.check_streak_achievements(self.user)
        
        achievements = UserAchievement.objects.filter(user=self.user)
        achievement_types = [a.achievement_type for a in achievements]
        
        self.assertIn('streak_7', achievement_types)
        self.assertIn('streak_30', achievement_types)
        self.assertNotIn('streak_100', achievement_types)


# ========================
# API ENDPOINT TESTS
# ========================

class GamificationAPITestCase(APITestCase):
    """Test Gamification API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_register_activity_endpoint(self):
        """Test POST /gamification/activity/"""
        response = self.client.post('/api/gamification/activity/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('streak', response.data)
        self.assertIn('best_streak', response.data)
    
    def test_get_current_streak_endpoint(self):
        """Test GET /gamification/streak/"""
        StreakService.register_activity(self.user)
        
        response = self.client.get('/api/gamification/streak/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('streak', response.data)
        self.assertIn('best_streak', response.data)
        self.assertIn('last_practice_date', response.data)
    
    def test_get_user_points_endpoint(self):
        """Test GET /gamification/points/"""
        self.user.total_points = 500
        self.user.save()
        
        response = self.client.get('/api/gamification/points/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_points'], 500)
    
    def test_add_points_endpoint_success(self):
        """Test POST /gamification/points/add/ with valid data"""
        response = self.client.post(
            '/api/gamification/points/add/',
            {'amount': 100},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_points'], 100)
    
    def test_add_points_endpoint_invalid_amount(self):
        """Test POST /gamification/points/add/ with invalid amount"""
        response = self.client.post(
            '/api/gamification/points/add/',
            {'amount': 'invalid'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_add_points_endpoint_negative_amount(self):
        """Test POST /gamification/points/add/ with negative amount"""
        response = self.client.post(
            '/api/gamification/points/add/',
            {'amount': -50},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_user_achievements_endpoint(self):
        """Test GET /gamification/achievements/"""
        # Create some achievements
        UserAchievement.objects.create(
            user=self.user,
            achievement_type='points_1000'
        )
        UserAchievement.objects.create(
            user=self.user,
            achievement_type='streak_7'
        )
        
        response = self.client.get('/api/gamification/achievements/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('achievement_type', response.data[0])
        self.assertIn('achievement_name', response.data[0])
    
    def test_leaderboard_endpoint(self):
        """Test GET /gamification/leaderboard/"""
        # Create additional users with points
        user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='pass123'
        )
        user2.total_points = 1000
        user2.save()
        
        self.user.total_points = 500
        self.user.save()
        
        response = self.client.get('/api/gamification/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
        # Check ordering (highest points first)
        self.assertGreaterEqual(
            response.data[0]['total_points'],
            response.data[1]['total_points']
        )
    
    def test_endpoints_require_authentication(self):
        """Test that endpoints require authentication"""
        self.client.force_authenticate(user=None)
        
        endpoints = [
            '/api/gamification/activity/',
            '/api/gamification/streak/',
            '/api/gamification/points/',
            '/api/gamification/achievements/',
            '/api/gamification/leaderboard/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ========================
# INTEGRATION TESTS
# ========================

class GamificationIntegrationTestCase(TestCase):
    """Test integration between different gamification components"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_complete_user_journey(self):
        """Test a complete user journey through gamification system"""
        # Day 1: First activity and points
        StreakService.register_activity(self.user)
        PointsService.add_points(self.user, 100)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_streak, 1)
        self.assertEqual(self.user.total_points, 100)
        
        # Day 2: Continue streak and earn more points
        self.user.last_practice_date = date.today() - timedelta(days=1)
        self.user.save()
        
        StreakService.register_activity(self.user)
        PointsService.add_points(self.user, 200)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_streak, 2)
        self.assertEqual(self.user.total_points, 300)
        
        # Check daily statistics
        stats = DailyStatistic.objects.filter(user=self.user)
        self.assertEqual(stats.count(), 2)
    
    def test_achievement_unlocking_cascade(self):
        """Test that adding points unlocks multiple achievements at once"""
        PointsService.add_points(self.user, 10000)
        
        achievements = UserAchievement.objects.filter(user=self.user)
        achievement_types = [a.achievement_type for a in achievements]
        
        # Should unlock all three point achievements
        self.assertEqual(len(achievement_types), 3)
        self.assertIn('points_1000', achievement_types)
        self.assertIn('points_5000', achievement_types)
        self.assertIn('points_10000', achievement_types)
    
    def test_daily_statistics_aggregation(self):
        """Test that daily statistics properly aggregate multiple activities"""
        PointsService.add_points(self.user, 50)
        PointsService.add_points(self.user, 30)
        PointsService.add_points(self.user, 20)
        
        daily_stat = DailyStatistic.objects.get(
            user=self.user,
            date=date.today()
        )
        
        self.assertEqual(daily_stat.points_earned, 100)


# ========================
# MODEL TESTS
# ========================

class UserAchievementModelTestCase(TestCase):
    """Test UserAchievement model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_achievement_creation(self):
        """Test creating an achievement"""
        achievement = UserAchievement.objects.create(
            user=self.user,
            achievement_type='points_1000'
        )
        
        self.assertEqual(achievement.user, self.user)
        self.assertEqual(achievement.achievement_type, 'points_1000')
        self.assertIsNotNone(achievement.achieved_at)
    
    def test_achievement_unique_constraint(self):
        """Test that user cannot have duplicate achievements"""
        UserAchievement.objects.create(
            user=self.user,
            achievement_type='points_1000'
        )
        
        # Attempt to create duplicate
        with self.assertRaises(Exception):
            UserAchievement.objects.create(
                user=self.user,
                achievement_type='points_1000'
            )
    
    def test_achievement_display_name(self):
        """Test that achievement display name works correctly"""
        achievement = UserAchievement.objects.create(
            user=self.user,
            achievement_type='points_1000'
        )
        
        display_name = achievement.get_achievement_type_display()
        self.assertEqual(display_name, '1,000 puntos')


class DailyStatisticModelTestCase(TestCase):
    """Test DailyStatistic model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_daily_statistic_creation(self):
        """Test creating a daily statistic"""
        stat = DailyStatistic.objects.create(
            user=self.user,
            date=date.today(),
            phrases_practiced=10,
            correct_answers=8,
            points_earned=80
        )
        
        self.assertEqual(stat.user, self.user)
        self.assertEqual(stat.phrases_practiced, 10)
        self.assertEqual(stat.correct_answers, 8)
    
    def test_daily_statistic_unique_constraint(self):
        """Test that user can only have one stat per day"""
        DailyStatistic.objects.create(
            user=self.user,
            date=date.today()
        )
        
        # Attempt to create duplicate
        with self.assertRaises(Exception):
            DailyStatistic.objects.create(
                user=self.user,
                date=date.today()
            )
    
    def test_daily_statistic_ordering(self):
        """Test that daily statistics are ordered by date descending"""
        DailyStatistic.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=2)
        )
        DailyStatistic.objects.create(
            user=self.user,
            date=date.today()
        )
        DailyStatistic.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=1)
        )
        
        stats = DailyStatistic.objects.filter(user=self.user)
        dates = [stat.date for stat in stats]
        
        # Should be ordered newest first
        self.assertEqual(dates[0], date.today())
        self.assertEqual(dates[2], date.today() - timedelta(days=2))