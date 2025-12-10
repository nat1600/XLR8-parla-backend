from django.urls import path
from .views import GoogleLoginView, UserProfileView, LogoutView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
