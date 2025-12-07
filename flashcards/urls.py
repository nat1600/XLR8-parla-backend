# flashcards/urls.py

from django.urls import path
from .views import (
    FlashListCreateView,
    FlashDetailView,
    FlashcardsDueView,
    FlashcardAnswerView,
    StartPracticeSessionView,
    AddPracticeDetailView,
    CompletePracticeSessionView,
    PracticeSessionListView,
    PracticeSessionDetailView,
    MatchingStartView,
    MatchingCheckView,
    MatchingFinishView,
    TimedStartView,
    TimedAnswerView,
    TimedFinishView
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

    path('practice-sessions/start/', StartPracticeSessionView.as_view()),

    path('practice-sessions/', PracticeSessionListView.as_view()),

    path('practice-sessions/<int:id>/', PracticeSessionDetailView.as_view()),

    path('practice-sessions/<int:session_id>/detail/', AddPracticeDetailView.as_view()),

    path('practice-sessions/<int:session_id>/complete/', CompletePracticeSessionView.as_view()),


    # matching
    path('matching/start/', MatchingStartView.as_view(), name='matching-start'),
    path('matching/check/', MatchingCheckView.as_view(), name='matching-check'),
    path('matching/finish/', MatchingFinishView.as_view(), name='matching-finish'),

    #timed
    path('timed/start/', TimedStartView.as_view(), name='timed-start'),
    path('timed/answer/', TimedAnswerView.as_view(), name='timed-answer'),
    path('timed/finish/', TimedFinishView.as_view(), name='timed-finish'),

]
