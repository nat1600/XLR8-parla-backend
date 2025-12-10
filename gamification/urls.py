from django.urls import path
from .views import (
    RegisterActivityView,
    CurrentStreakView,
    UserPointsView,
    AddPointsView,
)


urlpatterns = [
    path("activity/", RegisterActivityView.as_view(), name="register-activity"),
    path("streak/", CurrentStreakView.as_view(), name="current-streak"),

    # Points URLs
    path("points/", UserPointsView.as_view(), name="user-points"),
    path("points/add/", AddPointsView.as_view(), name="add-points"),
]
