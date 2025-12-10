from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from phrases.models import Phrase, Language, Category
from phrases.serializers import (
    PhraseListSerializer,
    PhraseDetailSerializer,
    PhraseCreateSerializer,
)

User = get_user_model()


class TranslateViewTest(APITestCase):
    """Tests for TranslateView API endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.url = reverse('translate')  # Adjust according to your URL name
        
        # Create languages
        self.lang_en = Language.objects.create(code='en', name='English')
        self.lang_es = Language.objects.create(code='es', name='Spanish')
    
   
    
    @patch('phrases.views.TranslationService')
    def test_translate_success(self, mock_service):
        """Test successful translation"""
        self.client.force_authenticate(user=self.user)
        
        # Mock translation service response
        mock_instance = mock_service.return_value
        mock_instance.translate.return_value = {
            'original': 'dog',
            'translation': 'perro',
            'pronunciation': '/ˈpero/',
            'source_lang': 'en',
            'target_lang': 'es'
        }
        
        data = {
            'text': 'dog',
            'source_lang': 'en',
            'target_lang': 'es'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['original'], 'dog')
        self.assertEqual(response.data['translation'], 'perro')
        self.assertEqual(response.data['pronunciation'], '/ˈpero/')
        self.assertEqual(response.data['source_lang'], 'en')
        self.assertEqual(response.data['target_lang'], 'es')
    
    @patch('phrases.views.TranslationService')
    def test_translate_without_pronunciation(self, mock_service):
        """Test translation without pronunciation field"""
        self.client.force_authenticate(user=self.user)
        
        mock_instance = mock_service.return_value
        mock_instance.translate.return_value = {
            'original': 'hello',
            'translation': 'hola',
            'source_lang': 'en',
            'target_lang': 'es'
        }
        
        data = {
            'text': 'hello',
            'source_lang': 'en',
            'target_lang': 'es'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['pronunciation'])
    
    def test_translate_invalid_data(self):
        """Test translation with invalid data"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'text': '',  # Empty text
            'source_lang': 'en',
            'target_lang': 'es'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_translate_missing_fields(self):
        """Test translation with missing required fields"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'text': 'hello'
            # Missing source_lang and target_lang
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('phrases.views.TranslationService')
    def test_translate_service_failure(self, mock_service):
        """Test translation when service fails"""
        self.client.force_authenticate(user=self.user)
        
        mock_instance = mock_service.return_value
        mock_instance.translate.side_effect = Exception('Service unavailable')
        
        data = {
            'text': 'hello',
            'source_lang': 'en',
            'target_lang': 'es'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('detail', response.data)
        self.assertIn('error', response.data)


class PhraseViewSetTest(APITestCase):
    """Tests for PhraseViewSet API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Create languages
        self.lang_en = Language.objects.create(code='en', name='English')
        self.lang_es = Language.objects.create(code='es', name='Spanish')
        self.lang_fr = Language.objects.create(code='fr', name='French')
        
        # Create categories
        self.category_grammar = Category.objects.create(
            name='Past Tense',
            type='grammar'
        )
        self.category_theme = Category.objects.create(
            name='Travel',
            type='theme'
        )
        
        # Create phrases for user1
        self.phrase1 = Phrase.objects.create(
            user=self.user1,
            original_text='Hello world',
            translated_text='Hola mundo',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        self.phrase2 = Phrase.objects.create(
            user=self.user1,
            original_text='Good morning',
            translated_text='Buenos días',
            source_language=self.lang_en,
            target_language=self.lang_es,
            source_type='youtube'
        )
        
        # Create phrase for user2
        self.phrase3 = Phrase.objects.create(
            user=self.user2,
            original_text='Thank you',
            translated_text='Gracias',
            source_language=self.lang_en,
            target_language=self.lang_es
        )
        
        self.list_url = reverse('phrase-list')  # Adjust according to your URL name
    
    
    
    def test_list_phrases_authenticated(self):
        """Test listing phrases returns only current user's phrases"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only user1's phrases
        
        # Verify user2's phrase is not included
        phrase_ids = [p['id'] for p in response.data['results']]
        self.assertNotIn(self.phrase3.id, phrase_ids)
    
    def test_filter_by_source_language(self):
        """Test filtering phrases by source language"""
        self.client.force_authenticate(user=self.user1)
        
        # Create phrase with different source language
        Phrase.objects.create(
            user=self.user1,
            original_text='Bonjour',
            translated_text='Hello',
            source_language=self.lang_fr,
            target_language=self.lang_en
        )
        
        url = f"{self.list_url}?source_language={self.lang_en.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_by_target_language(self):
        """Test filtering phrases by target language"""
        self.client.force_authenticate(user=self.user1)
        
        url = f"{self.list_url}?target_language={self.lang_es.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_by_source_type(self):
        """Test filtering phrases by source type"""
        self.client.force_authenticate(user=self.user1)
        
        url = f"{self.list_url}?source_type=youtube"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['source_type'], 'youtube')
    
    def test_search_by_original_text(self):
        """Test searching phrases by original text"""
        self.client.force_authenticate(user=self.user1)
        
        url = f"{self.list_url}?search=morning"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('morning', response.data['results'][0]['original_text'].lower())
    
    def test_search_by_translated_text(self):
        """Test searching phrases by translated text"""
        self.client.force_authenticate(user=self.user1)
        
        url = f"{self.list_url}?search=Hola"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_ordering_by_created_at(self):
        """Test ordering phrases by creation date"""
        self.client.force_authenticate(user=self.user1)
        
        url = f"{self.list_url}?ordering=-created_at"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Most recent should be first (phrase2)
        self.assertEqual(response.data['results'][0]['id'], self.phrase2.id)
    
    def test_create_phrase(self):
        """Test creating a new phrase"""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'original_text': 'Good night',
            'translated_text': 'Buenas noches',
            'source_language': self.lang_en.id,
            'target_language': self.lang_es.id
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['original_text'], 'Good night')
        self.assertEqual(response.data['translated_text'], 'Buenas noches')
        
        # Verify phrase was created with correct user
        phrase = Phrase.objects.get(id=response.data['id'])
        self.assertEqual(phrase.user, self.user1)
    
    
    
    def test_create_phrase_with_optional_fields(self):
        """Test creating a phrase with optional fields"""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'original_text': 'Hello',
            'translated_text': 'Hola',
            'pronunciation': '/əˈloʊ/',
            'source_language': self.lang_en.id,
            'target_language': self.lang_es.id,
            'source_type': 'netflix',
            'source_url': 'https://example.com',
            'context': 'Greeting in a formal setting'
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['pronunciation'], '/əˈloʊ/')
        self.assertEqual(response.data['source_type'], 'netflix')
    

    
    def test_retrieve_phrase(self):
        """Test retrieving a specific phrase"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('phrase-detail', kwargs={'pk': self.phrase1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.phrase1.id)
        self.assertEqual(response.data['original_text'], 'Hello world')
    
    def test_retrieve_other_users_phrase(self):
        """Test that users cannot retrieve other users' phrases"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('phrase-detail', kwargs={'pk': self.phrase3.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_phrase(self):
        """Test updating a phrase"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('phrase-detail', kwargs={'pk': self.phrase1.id})
        data = {
            'original_text': 'Hello everyone',
            'translated_text': 'Hola a todos',
            'source_language': self.lang_en.id,
            'target_language': self.lang_es.id
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['original_text'], 'Hello everyone')
        
        self.phrase1.refresh_from_db()
        self.assertEqual(self.phrase1.original_text, 'Hello everyone')
    
    def test_partial_update_phrase(self):
        """Test partially updating a phrase"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('phrase-detail', kwargs={'pk': self.phrase1.id})
        data = {
            'pronunciation': '/həˈloʊ/'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.phrase1.refresh_from_db()
        self.assertEqual(self.phrase1.pronunciation, '/həˈloʊ/')
        self.assertEqual(self.phrase1.original_text, 'Hello world')  # Unchanged
    
    def test_delete_phrase(self):
        """Test deleting a phrase"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('phrase-detail', kwargs={'pk': self.phrase1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Phrase.objects.filter(id=self.phrase1.id).exists())
    
    def test_delete_other_users_phrase(self):
        """Test that users cannot delete other users' phrases"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('phrase-detail', kwargs={'pk': self.phrase3.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Phrase.objects.filter(id=self.phrase3.id).exists())



class CategoryViewSetTest(APITestCase):
    """Tests for CategoryViewSet API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create categories
        self.category1 = Category.objects.create(
            name='Past Tense',
            type='grammar',
            description='Phrases about past tense'
        )
        self.category2 = Category.objects.create(
            name='Present Perfect',
            type='grammar',
            description='Phrases about present perfect'
        )
        self.category3 = Category.objects.create(
            name='Travel',
            type='theme',
            description='Travel-related phrases'
        )
        self.category4 = Category.objects.create(
            name='Food',
            type='theme',
            description='Food-related phrases'
        )
        
        self.list_url = reverse('category-list')  # Adjust according to your URL name
    

    
    def test_list_categories_authenticated(self):
        """Test listing all categories"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
    
    def test_categories_ordered_by_name(self):
        """Test that categories are ordered alphabetically by name"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [cat['name'] for cat in response.data['results']]
        self.assertEqual(names, sorted(names))
    
    def test_filter_categories_by_grammar_type(self):
        """Test filtering categories by grammar type"""
        self.client.force_authenticate(user=self.user)
        
        url = f"{self.list_url}?type=grammar"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        for category in response.data['results']:
            self.assertEqual(category['type'], 'grammar')
    
    def test_filter_categories_by_theme_type(self):
        """Test filtering categories by theme type"""
        self.client.force_authenticate(user=self.user)
        
        url = f"{self.list_url}?type=theme"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        for category in response.data['results']:
            self.assertEqual(category['type'], 'theme')
    
    def test_retrieve_category(self):
        """Test retrieving a specific category"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.category1.id)
        self.assertEqual(response.data['name'], 'Past Tense')
        self.assertEqual(response.data['type'], 'grammar')
    
    def test_cannot_create_category(self):
        """Test that categories are read-only (cannot create)"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'name': 'Future Tense',
            'type': 'grammar'
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_cannot_update_category(self):
        """Test that categories are read-only (cannot update)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        data = {
            'name': 'Updated Name',
            'type': 'grammar'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_cannot_delete_category(self):
        """Test that categories are read-only (cannot delete)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('category-detail', kwargs={'pk': self.category1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Category.objects.filter(id=self.category1.id).exists())


class ViewIntegrationTest(APITestCase):
    """Integration tests for views working together"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.lang_en = Language.objects.create(code='en', name='English')
        self.lang_es = Language.objects.create(code='es', name='Spanish')
        
        self.category = Category.objects.create(
            name='Greetings',
            type='theme'
        )
        
        self.client.force_authenticate(user=self.user)
    

    
    def test_create_phrase_with_category_then_filter(self):
        """Test creating phrases with categories and then filtering by them"""
        # Create phrases with different categories
        phrase1_data = {
            'original_text': 'Hello',
            'translated_text': 'Hola',
            'source_language': self.lang_en.id,
            'target_language': self.lang_es.id,
            'categories': [self.category.id]
        }
        
        phrase_url = reverse('phrase-list')
        response1 = self.client.post(phrase_url, phrase1_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Create phrase without category
        phrase2_data = {
            'original_text': 'Thank you',
            'translated_text': 'Gracias',
            'source_language': self.lang_en.id,
            'target_language': self.lang_es.id
        }
        
        response2 = self.client.post(phrase_url, phrase2_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # List all phrases
        list_response = self.client.get(phrase_url)
        self.assertEqual(len(list_response.data['results']), 2)