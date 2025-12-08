# flashcards/urls.py

from django.urls import path
from .views import (
    FlashListCreateView,
    FlashDetailView,
    FlashcardsDueView,
    FlashcardAnswerView
)

urlpatterns = [
    # List and create flashcar
    path('', FlashListCreateView.as_view(), name='flashcard-list-create'),

    # CRUD only one flashcard
    path('<int:pk>/', FlashDetailView.as_view(), name='flashcard-detail'),

    # Flashcards  (due)
    path('due/', FlashcardsDueView.as_view(), name='flashcards-due'),

    #  Answer a flashcard(SM-2)
    path('<int:phrase_id>/answer/', FlashcardAnswerView.as_view(), name='flashcard-answer'),
]
