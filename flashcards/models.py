from django.db import models
from django.conf import settings
from django.utils import timezone

class FlashcardReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcard_reviews')
    phrase = models.ForeignKey('phrases.Phrase', on_delete=models.CASCADE, related_name='flashcard_reviews')

    # SM-2 CORE FIELDS
    repetitions = models.IntegerField(default=0)  
    interval = models.IntegerField(default=1)     
    ef = models.FloatField(default=2.5)           

    next_review_date = models.DateTimeField(default=timezone.now)

    # STATISTICS
    total_reviews = models.IntegerField(default=0)
    correct_reviews = models.IntegerField(default=0)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flashcard_reviews'
        unique_together = ['user', 'phrase']
    
    def __str__(self):
        return f"{self.user.username} - {self.phrase.original_text[:30]}"


class PracticeSession(models.Model):
    SESSION_TYPES = [
        ('flashcard', 'Flashcards'),
        ('timed', 'Contrarreloj'),
        ('matching', 'Emparejar'),
        ('quiz', 'Quiz'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_sessions')
    session_type = models.CharField(max_length=50, choices=SESSION_TYPES)

    mode_data = models.JSONField(default=dict, blank = True)

    phrases_practiced = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    duration_seconds = models.IntegerField(default=0)

    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'practice_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_type}"


class PracticeSessionDetail(models.Model):
    practice_session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name='details')
    phrase = models.ForeignKey('phrases.Phrase', on_delete=models.CASCADE, related_name='practice_details')
    was_correct = models.BooleanField()
    response_time_seconds = models.IntegerField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'practice_session_details'
    
    def __str__(self):
        return f"{'✓' if self.was_correct else '✗'} {self.phrase.original_text[:30]}"