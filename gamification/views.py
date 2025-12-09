# gamification/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model


from gamification.services.streak_service import StreakService
from gamification.models import UserAchievement
from gamification.serializers import AchievementSerializer

from rest_framework.generics import ListAPIView
from gamification.serializers import LeaderboardSerializer

from gamification.services.points_service import PointsService
from rest_framework import status


from datetime import date, timedelta
from gamification.models import DailyStatistic
from gamification.serializers import DailyStatisticSerializer

User = get_user_model()

class RegisterActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = StreakService.register_activity(request.user)
        return Response(result, status=200)


class CurrentStreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "streak": user.current_streak,
            "best_streak": user.longest_streak,
            "last_practice_date": user.last_practice_date
        }, status=200)


# Poins service view
class UserPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "total_points": request.user.total_points
        })


class AddPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_amount = request.data.get("amount")

        try:
            amount = int(raw_amount)
        except (TypeError, ValueError):
            return Response(
                {"error": "El valor 'amount' debe ser un número entero."},
                status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response(
                {"error": "El valor 'amount' debe ser mayor a 0."},
            status=status.HTTP_400_BAD_REQUEST
            )

        total = PointsService.add_points(request.user, amount)
        return Response({"total_points": total}, status=status.HTTP_200_OK)




class UserAchievementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        achievements = UserAchievement.objects.filter(
            user=request.user
        ).order_by("-achieved_at")

        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)



class LeaderboardView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        return User.objects.order_by("-total_points")
    






class DailyStatsChartView(APIView):
    """
    Get daily statistics for chart visualization.
    
    ENDPOINT:
        GET /api/gamification/daily-stats/?days=7
    
    QUERY PARAMS:
        - days: Number of days to retrieve (default: 7, max: 90)
    
    RESPONSE FORMAT:
        [
            {
                "id": 1,
                "user": "username",
                "date": "2024-12-09",
                "phrases_practiced": 25,
                "correct_answers": 20,
                "practice_minutes": 15,
                "points_earned": 100,
                "streak_maintained": true,
                "accuracy": 80.0
            },
            ...
        ]
    
    EXAMPLE:
        GET /api/gamification/daily-stats/?days=30
        → Returns last 30 days of practice data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get days parameter from query string, default to 7
        try:
            days = int(request.query_params.get('days', 7))
            # Limit to reasonable maximum
            days = min(days, 90)
        except (TypeError, ValueError):
            days = 7

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)

        # Query daily statistics for the date range
        stats = DailyStatistic.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        serializer = DailyStatisticSerializer(stats, many=True)
        
        return Response({
            "start_date": start_date,
            "end_date": end_date,
            "total_days": days,
            "data": serializer.data
        })


class WeeklyStatsView(APIView):
    """
    Get aggregated weekly statistics.
    
    ENDPOINT:
        GET /api/gamification/weekly-stats/?weeks=4
    
    QUERY PARAMS:
        - weeks: Number of weeks to retrieve (default: 4, max: 52)
    
    RESPONSE FORMAT:
        [
            {
                "week_start": "2024-12-03",
                "week_end": "2024-12-09",
                "total_phrases": 150,
                "total_correct": 120,
                "total_minutes": 90,
                "total_points": 500,
                "days_practiced": 5,
                "average_accuracy": 80.0
            },
            ...
        ]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request): # Get weeks parameter
        try:
            weeks = int(request.query_params.get('weeks', 4)) # Default to 4 weeks
            weeks = min(weeks, 52) # Max 52 weeks
        except (TypeError, ValueError):
            weeks = 4

        end_date = date.today() 
        start_date = end_date - timedelta(weeks=weeks*7)

        # Get all daily stats in range
        stats = DailyStatistic.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        # Group by week
        weekly_data = []
        current_week = []
        week_start = None

        for stat in stats:
            if week_start is None:
                week_start = stat.date
            
            # Check if we're still in the same week
            if (stat.date - week_start).days < 7:
                current_week.append(stat)
            else:
                # Process completed week
                if current_week:
                    weekly_data.append(self._aggregate_week(current_week, week_start))
                
                # Start new week
                week_start = stat.date
                current_week = [stat]
        
        # Add last week if exists
        if current_week:
            weekly_data.append(self._aggregate_week(current_week, week_start))

        return Response({
            "weeks": len(weekly_data),
            "data": weekly_data
        })

    def _aggregate_week(self, stats, week_start):
        """Helper to aggregate weekly statistics"""
        total_phrases = sum(s.phrases_practiced for s in stats)
        total_correct = sum(s.correct_answers for s in stats)
        total_minutes = sum(s.practice_minutes for s in stats)
        total_points = sum(s.points_earned for s in stats)
        
        accuracy = 0
        if total_phrases > 0:
            accuracy = round((total_correct / total_phrases) * 100, 2)

        return {
            "week_start": week_start,
            "week_end": week_start + timedelta(days=6),
            "total_phrases": total_phrases,
            "total_correct": total_correct,
            "total_minutes": total_minutes,
            "total_points": total_points,
            "days_practiced": len(stats),
            "average_accuracy": accuracy
        }


class MonthlyStatsView(APIView):
    """
    Get aggregated monthly statistics.
    
    ENDPOINT:
        GET /api/gamification/monthly-stats/?months=6
    
    QUERY PARAMS:
        - months: Number of months to retrieve (default: 6, max: 12)
    
    RESPONSE FORMAT:
        [
            {
            "month": 12,
            "year": 2024,
            "month_name": "December",
            "total_phrases": 500,
            "total_correct": 400,
            "total_points": 2000,
            "days_active": 20,
            "average_accuracy": 80.0
            },
            ...
        ]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request): # Get months parameter
        try:
            months = int(request.query_params.get('months', 6))
            months = min(months, 12)
        except (TypeError, ValueError):
            months = 6

        today = date.today()
        monthly_data = []

        for i in range(months):
            # Calculate month
            target_month = today.month - i # 0 = current month
            target_year = today.year
            
            while target_month < 1: # Adjust year if month < 1
                target_month += 12
                target_year -= 1

            # Get stats for this month
            stats = DailyStatistic.objects.filter(
                user=request.user,
                date__year=target_year,
                date__month=target_month
            )

            total_phrases = sum(s.phrases_practiced for s in stats)
            total_correct = sum(s.correct_answers for s in stats)
            total_points = sum(s.points_earned for s in stats)
            days_active = stats.count()

            accuracy = 0
            if total_phrases > 0:
                accuracy = round((total_correct / total_phrases) * 100, 2)

            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]

            monthly_data.append({
                "month": target_month,
                "year": target_year,
                "month_name": month_names[target_month - 1],
                "total_phrases": total_phrases,
                "total_correct": total_correct,
                "total_points": total_points,
                "days_active": days_active,
                "average_accuracy": accuracy
            })

        # Reverse to show oldest first
        monthly_data.reverse()

        return Response({
            "months": len(monthly_data),
            "data": monthly_data
        })
