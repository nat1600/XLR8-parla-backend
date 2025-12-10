from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import FlashcardReview, PracticeSession, PracticeSessionDetail
from phrases.models import Phrase, Language, Category

User = get_user_model()


class FlashcardReviewModelTest(TestCase):
    """Tests for FlashcardReview model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create languages first
        self.lang_en = Language.objects.create(
            code='en',
            name='English'
        )
        self.lang_es = Language.objects.create(
            code='es',
            name='Spanish'
        )
        self.phrase = Phrase.objects.create(
            user=self.user,
            original_text='Hello world',
            translated_text='Hola mundo',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
    
    def test_create_flashcard_review(self):
        """Test creating a flashcard review with default values"""
        review = FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        
        self.assertEqual(review.repetitions, 0)
        self.assertEqual(review.interval, 1)
        self.assertEqual(review.ef, 2.5)
        self.assertEqual(review.total_reviews, 0)
        self.assertEqual(review.correct_reviews, 0)
        self.assertIsNotNone(review.next_review_date)
        self.assertIsNone(review.last_reviewed_at)
    
    def test_flashcard_review_str(self):
        """Test string representation of the model"""
        review = FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        
        expected = f"{self.user.username} - {self.phrase.original_text[:30]}"
        self.assertEqual(str(review), expected)
    
    def test_unique_together_constraint(self):
        """Test that two reviews cannot be created for the same user and phrase"""
        FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            FlashcardReview.objects.create(
                user=self.user,
                phrase=self.phrase
            )
    
    def test_update_sm2_fields(self):
        """Test updating SM-2 algorithm fields"""
        review = FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        
        review.repetitions = 3
        review.interval = 7
        review.ef = 2.8
        review.save()
        
        review.refresh_from_db()
        self.assertEqual(review.repetitions, 3)
        self.assertEqual(review.interval, 7)
        self.assertEqual(review.ef, 2.8)
    
    def test_update_statistics(self):
        """Test updating review statistics"""
        review = FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        
        review.total_reviews = 5
        review.correct_reviews = 3
        review.last_reviewed_at = timezone.now()
        review.save()
        
        review.refresh_from_db()
        self.assertEqual(review.total_reviews, 5)
        self.assertEqual(review.correct_reviews, 3)
        self.assertIsNotNone(review.last_reviewed_at)
    
    def test_next_review_date_update(self):
        """Test updating next review date"""
        review = FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        
        future_date = timezone.now() + timedelta(days=3)
        review.next_review_date = future_date
        review.save()
        
        review.refresh_from_db()
        self.assertAlmostEqual(
            review.next_review_date.timestamp(),
            future_date.timestamp(),
            delta=1
        )
    
    def test_related_name_from_user(self):
        """Test accessing reviews from user"""
        FlashcardReview.objects.create(user=self.user, phrase=self.phrase)
        
        reviews = self.user.flashcard_reviews.all()
        self.assertEqual(reviews.count(), 1)
        self.assertEqual(reviews.first().phrase, self.phrase)
    
    def test_related_name_from_phrase(self):
        """Test accessing reviews from phrase"""
        FlashcardReview.objects.create(user=self.user, phrase=self.phrase)
        
        reviews = self.phrase.flashcard_reviews.all()
        self.assertEqual(reviews.count(), 1)
        self.assertEqual(reviews.first().user, self.user)


class PracticeSessionModelTest(TestCase):
    """Tests for PracticeSession model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_practice_session(self):
        """Test creating a practice session with default values"""
        session = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard'
        )
        
        self.assertEqual(session.session_type, 'flashcard')
        self.assertEqual(session.phrases_practiced, 0)
        self.assertEqual(session.correct_answers, 0)
        self.assertEqual(session.incorrect_answers, 0)
        self.assertEqual(session.points_earned, 0)
        self.assertEqual(session.duration_seconds, 0)
        self.assertFalse(session.completed)
        self.assertIsNotNone(session.started_at)
        self.assertIsNone(session.completed_at)
        self.assertEqual(session.mode_data, {})
    
    def test_practice_session_str(self):
        """Test string representation of the model"""
        session = PracticeSession.objects.create(
            user=self.user,
            session_type='timed'
        )
        
        expected = f"{self.user.username} - timed"
        self.assertEqual(str(session), expected)
    
    def test_all_session_types(self):
        """Test creating sessions of all available types"""
        types = ['flashcard', 'timed', 'matching', 'quiz']
        
        for session_type in types:
            session = PracticeSession.objects.create(
                user=self.user,
                session_type=session_type
            )
            self.assertEqual(session.session_type, session_type)
    
    def test_mode_data_json_field(self):
        """Test storing additional data in mode_data"""
        mode_data = {
            'difficulty': 'hard',
            'time_limit': 60,
            'categories': ['verbs', 'nouns']
        }
        
        session = PracticeSession.objects.create(
            user=self.user,
            session_type='quiz',
            mode_data=mode_data
        )
        
        session.refresh_from_db()
        self.assertEqual(session.mode_data['difficulty'], 'hard')
        self.assertEqual(session.mode_data['time_limit'], 60)
        self.assertEqual(len(session.mode_data['categories']), 2)
    
    def test_complete_session(self):
        """Test completing a practice session"""
        session = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard'
        )
        
        session.phrases_practiced = 10
        session.correct_answers = 7
        session.incorrect_answers = 3
        session.points_earned = 70
        session.duration_seconds = 300
        session.completed = True
        session.completed_at = timezone.now()
        session.save()
        
        session.refresh_from_db()
        self.assertTrue(session.completed)
        self.assertEqual(session.phrases_practiced, 10)
        self.assertEqual(session.correct_answers, 7)
        self.assertEqual(session.incorrect_answers, 3)
        self.assertIsNotNone(session.completed_at)
    
    def test_session_ordering(self):
        """Test that sessions are ordered by start date (most recent first)"""
        session1 = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard'
        )
        
        # Wait a moment to ensure different timestamp
        import time
        time.sleep(0.01)
        
        session2 = PracticeSession.objects.create(
            user=self.user,
            session_type='quiz'
        )
        
        sessions = PracticeSession.objects.all()
        self.assertEqual(sessions.first(), session2)
        self.assertEqual(sessions.last(), session1)
    
    def test_related_name_from_user(self):
        """Test accessing sessions from user"""
        PracticeSession.objects.create(user=self.user, session_type='flashcard')
        PracticeSession.objects.create(user=self.user, session_type='quiz')
        
        sessions = self.user.practice_sessions.all()
        self.assertEqual(sessions.count(), 2)


class PracticeSessionDetailModelTest(TestCase):
    """Tests for PracticeSessionDetail model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create languages first
        self.lang_en = Language.objects.create(
            code='en',
            name='English'
        )
        self.lang_es = Language.objects.create(
            code='es',
            name='Spanish'
        )
        self.phrase = Phrase.objects.create(
            user=self.user,
            original_text='Good morning',
            translated_text='Buenos días',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        self.session = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard'
        )
    
    def test_create_practice_detail_correct(self):
        """Test creating a practice detail with correct answer"""
        detail = PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True,
            response_time_seconds=5
        )
        
        self.assertTrue(detail.was_correct)
        self.assertEqual(detail.response_time_seconds, 5)
        self.assertIsNotNone(detail.answered_at)
    
    def test_create_practice_detail_incorrect(self):
        """Test creating a practice detail with incorrect answer"""
        detail = PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=False,
            response_time_seconds=10
        )
        
        self.assertFalse(detail.was_correct)
        self.assertEqual(detail.response_time_seconds, 10)
    
    def test_practice_detail_str(self):
        """Test string representation of the model"""
        detail = PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        expected = f"✓ {self.phrase.original_text[:30]}"
        self.assertEqual(str(detail), expected)
        
        detail_incorrect = PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=False
        )
        
        expected_incorrect = f"✗ {self.phrase.original_text[:30]}"
        self.assertEqual(str(detail_incorrect), expected_incorrect)
    
    def test_response_time_optional(self):
        """Test that response time is optional"""
        detail = PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        self.assertIsNone(detail.response_time_seconds)
    
    def test_multiple_details_per_session(self):
        """Test creating multiple details for a session"""
        phrase2 = Phrase.objects.create(
            user=self.user,
            original_text='Thank you',
            translated_text='Gracias',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        
        PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=phrase2,
            was_correct=False
        )
        
        details = self.session.details.all()
        self.assertEqual(details.count(), 2)
    
    def test_related_name_from_session(self):
        """Test accessing details from session"""
        PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        details = self.session.details.all()
        self.assertEqual(details.count(), 1)
        self.assertEqual(details.first().phrase, self.phrase)
    
    def test_related_name_from_phrase(self):
        """Test accessing details from phrase"""
        PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        details = self.phrase.practice_details.all()
        self.assertEqual(details.count(), 1)
        self.assertEqual(details.first().practice_session, self.session)
    
    def test_cascade_delete_session(self):
        """Test that deleting a session deletes its details"""
        PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        self.assertEqual(PracticeSessionDetail.objects.count(), 1)
        
        self.session.delete()
        
        self.assertEqual(PracticeSessionDetail.objects.count(), 0)
    
    def test_cascade_delete_phrase(self):
        """Test that deleting a phrase deletes its details"""
        PracticeSessionDetail.objects.create(
            practice_session=self.session,
            phrase=self.phrase,
            was_correct=True
        )
        
        self.assertEqual(PracticeSessionDetail.objects.count(), 1)
        
        self.phrase.delete()
        
        self.assertEqual(PracticeSessionDetail.objects.count(), 0)


class PhraseOptionalFieldsTest(TestCase):
    """Tests for Phrase optional fields"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lang_en = Language.objects.create(code='en', name='English')
        self.lang_es = Language.objects.create(code='es', name='Spanish')
    
    def test_phrase_with_pronunciation(self):
        """Test creating phrase with pronunciation"""
        phrase = Phrase.objects.create(
            user=self.user,
            original_text='Hello',
            translated_text='Hola',
            pronunciation='/həˈloʊ/',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        
        self.assertEqual(phrase.pronunciation, '/həˈloʊ/')
    
    def test_phrase_with_source_url(self):
        """Test creating phrase with source URL"""
        phrase = Phrase.objects.create(
            user=self.user,
            original_text='Hello',
            translated_text='Hola',
            source_url='https://example.com/video',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        
        self.assertEqual(phrase.source_url, 'https://example.com/video')
    
    def test_phrase_with_all_source_types(self):
        """Test creating phrases with all source types"""
        source_types = ['youtube', 'netflix', 'web', 'pdf']
        
        for source_type in source_types:
            phrase = Phrase.objects.create(
                user=self.user,
                original_text=f'Text from {source_type}',
                translated_text=f'Texto de {source_type}',
                source_type=source_type,
                source_language=self.lang_en,
                target_language=self.lang_es
            )
            self.assertEqual(phrase.source_type, source_type)
    
    def test_phrase_with_context(self):
        """Test creating phrase with context"""
        context = "This phrase was used in a conversation about weather"
        phrase = Phrase.objects.create(
            user=self.user,
            original_text='It\'s raining',
            translated_text='Está lloviendo',
            context=context,
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        
        self.assertEqual(phrase.context, context)
    
    def test_phrase_without_optional_fields(self):
        """Test creating phrase without optional fields"""
        phrase = Phrase.objects.create(
            user=self.user,
            original_text='Hello',
            translated_text='Hola',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        
        self.assertIsNone(phrase.pronunciation)
        self.assertIsNone(phrase.source_url)
        self.assertIsNone(phrase.source_type)
        self.assertIsNone(phrase.context)


class PhraseCategoryRelationTest(TestCase):
    """Tests for Phrase-Category ManyToMany relationship"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lang_en = Language.objects.create(code='en', name='English')
        self.lang_es = Language.objects.create(code='es', name='Spanish')
        
        self.category_grammar = Category.objects.create(
            name='Past Tense',
            type='grammar',
            description='Phrases about past tense'
        )
        self.category_theme = Category.objects.create(
            name='Travel',
            type='theme',
            description='Phrases related to travel'
        )
        
        self.phrase = Phrase.objects.create(
            user=self.user,
            original_text='I went to the beach',
            translated_text='Fui a la playa',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
    
    def test_add_single_category_to_phrase(self):
        """Test adding a single category to a phrase"""
        self.phrase.categories.add(self.category_grammar)
        
        self.assertEqual(self.phrase.categories.count(), 1)
        self.assertIn(self.category_grammar, self.phrase.categories.all())
    
    def test_add_multiple_categories_to_phrase(self):
        """Test adding multiple categories to a phrase"""
        self.phrase.categories.add(self.category_grammar, self.category_theme)
        
        self.assertEqual(self.phrase.categories.count(), 2)
        self.assertIn(self.category_grammar, self.phrase.categories.all())
        self.assertIn(self.category_theme, self.phrase.categories.all())
    
    def test_remove_category_from_phrase(self):
        """Test removing a category from a phrase"""
        self.phrase.categories.add(self.category_grammar, self.category_theme)
        self.assertEqual(self.phrase.categories.count(), 2)
        
        self.phrase.categories.remove(self.category_grammar)
        
        self.assertEqual(self.phrase.categories.count(), 1)
        self.assertNotIn(self.category_grammar, self.phrase.categories.all())
        self.assertIn(self.category_theme, self.phrase.categories.all())
    
    def test_access_phrases_from_category(self):
        """Test accessing phrases from a category"""
        self.phrase.categories.add(self.category_grammar)
        
        phrase2 = Phrase.objects.create(
            user=self.user,
            original_text='I studied',
            translated_text='Estudié',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        phrase2.categories.add(self.category_grammar)
        
        phrases = self.category_grammar.phrases.all()
        self.assertEqual(phrases.count(), 2)
        self.assertIn(self.phrase, phrases)
        self.assertIn(phrase2, phrases)
    
    def test_phrase_without_categories(self):
        """Test phrase without any categories"""
        self.assertEqual(self.phrase.categories.count(), 0)
    
    def test_clear_all_categories(self):
        """Test clearing all categories from a phrase"""
        self.phrase.categories.add(self.category_grammar, self.category_theme)
        self.assertEqual(self.phrase.categories.count(), 2)
        
        self.phrase.categories.clear()
        
        self.assertEqual(self.phrase.categories.count(), 0)
    
    def test_category_types(self):
        """Test both category types (grammar and theme)"""
        self.assertEqual(self.category_grammar.type, 'grammar')
        self.assertEqual(self.category_theme.type, 'theme')


class IntegrationTest(TestCase):
    """Integration tests between models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lang_en = Language.objects.create(code='en', name='English')
        self.lang_es = Language.objects.create(code='es', name='Spanish')
        
        self.phrase = Phrase.objects.create(
            user=self.user,
            original_text='Hello',
            translated_text='Hola',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
    
    def test_complete_practice_workflow(self):
        """Test complete practice session workflow"""
        # Create session
        session = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard'
        )
        
        # Add details
        detail = PracticeSessionDetail.objects.create(
            practice_session=session,
            phrase=self.phrase,
            was_correct=True,
            response_time_seconds=3
        )
        
        # Update flashcard review
        review = FlashcardReview.objects.create(
            user=self.user,
            phrase=self.phrase
        )
        review.total_reviews = 1
        review.correct_reviews = 1
        review.last_reviewed_at = timezone.now()
        review.save()
        
        # Complete session
        session.phrases_practiced = 1
        session.correct_answers = 1
        session.points_earned = 10
        session.completed = True
        session.completed_at = timezone.now()
        session.save()
        
        # Verify everything is connected
        self.assertEqual(session.details.count(), 1)
        self.assertEqual(review.total_reviews, 1)
        self.assertTrue(session.completed)
    
    def test_user_statistics_calculation(self):
        """Test user statistics calculation"""
        # Create multiple sessions
        session1 = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard',
            correct_answers=7,
            incorrect_answers=3,
            completed=True
        )
        
        session2 = PracticeSession.objects.create(
            user=self.user,
            session_type='quiz',
            correct_answers=5,
            incorrect_answers=5,
            completed=True
        )
        
        # Calculate statistics
        total_sessions = self.user.practice_sessions.filter(completed=True).count()
        total_correct = sum(s.correct_answers for s in self.user.practice_sessions.all())
        total_incorrect = sum(s.incorrect_answers for s in self.user.practice_sessions.all())
        
        self.assertEqual(total_sessions, 2)
        self.assertEqual(total_correct, 12)
        self.assertEqual(total_incorrect, 8)
    
    def test_phrase_with_categories_in_practice(self):
        """Test using phrases with categories in practice sessions"""
        # Create categories
        category = Category.objects.create(
            name='Greetings',
            type='theme',
            description='Common greetings'
        )
        
        # Add category to phrase
        self.phrase.categories.add(category)
        
        # Create practice session
        session = PracticeSession.objects.create(
            user=self.user,
            session_type='flashcard',
            mode_data={'category': 'Greetings'}
        )
        
        # Add practice detail
        PracticeSessionDetail.objects.create(
            practice_session=session,
            phrase=self.phrase,
            was_correct=True
        )
        
        # Verify
        self.assertEqual(session.details.count(), 1)
        self.assertEqual(session.details.first().phrase.categories.count(), 1)
        self.assertEqual(session.mode_data['category'], 'Greetings')