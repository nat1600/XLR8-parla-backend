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