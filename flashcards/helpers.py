import random
from django.utils import timezone
from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from phrases.models import Phrase
from .models import PracticeSession, PracticeSessionDetail, FlashcardReview
from .serializers import PracticeSessionSerializer, PracticeSessionDetailSerializer

def choose_phrases_for_user(user, count):
    qs = Phrase.objects.filter(user=user)
    total = qs.count()
    
    if total >= count:
        ids = list(qs.values_list('id', flat=True))
        chosen_ids = random.sample(ids, count)
        return list(Phrase.objects.filter(id__in=chosen_ids))

    ids = list(Phrase.objects.all().values_list('id', flat=True))
    if len(ids) == 0:
        return []
    chosen_ids = random.choices(ids, k=min(count, len(ids)))
    return list(Phrase.objects.filter(id__in=chosen_ids))


def award_points_for_answer(session, was_correct, base=10):
    if was_correct:
        session.points_earned += base
    else:
        session.points_earned += 0