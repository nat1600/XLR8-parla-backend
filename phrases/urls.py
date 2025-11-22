# phrases/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhraseViewSet, TranslateView

router = DefaultRouter()
router.register('', PhraseViewSet, basename='phrase')

urlpatterns = [
    path('translate/', TranslateView.as_view(), name='translate'),
    path('', include(router.urls)),
]
