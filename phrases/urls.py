# phrases/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PhraseViewSet,
    TranslateView,
    CategoryViewSet,
    
)

router = DefaultRouter()

router.register(r'phrases', PhraseViewSet, basename='phrase')
router.register(r'categories', CategoryViewSet, basename='category')


urlpatterns = [
    path('translate/', TranslateView.as_view(), name='translate'),
    path('', include(router.urls)),
]
