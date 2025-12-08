from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, permissions, viewsets
from .serializers import (
    LanguageSerializer,
    CategorySerializer,
    PhraseListSerializer,
    PhraseDetailSerializer,
    PhraseCreateSerializer,
    TranslateRequestSerializer,
    TranslateResponseSerializer,
)
from .services.translation_service import TranslationService
from .models import Phrase, Language, Category
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class TranslateView(APIView):

    """
    Real-time text translation endpoint
    POST /api/phrases/translate/
    }
    Example: 
        Request:  {"text": "dog", "source_lang": "en", "target_lang": "es"}
        Response: {"original": "dog", "translation": "perro", "pronunciation": null, "source_lang": "en", "target_lang": "es"}

     Response Codes:
        - 200: Successful translation
        - 400: Invalid input data
        - 503: Translation service unavailable
    """
    
    permission_classes = [IsAuthenticated]  
    def post(self, request):
        print(" RAW DATA:", request.data)
        serializer = TranslateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        text = data["text"]
        source_lang = data["source_lang"]
        target_lang = data["target_lang"]

        service = TranslationService()

        try:
            result = service.translate(text, source_lang, target_lang)
        except Exception as e:
            return Response(
                {"detail": "Translation failed", "error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        response_data = {
            "original": result["original"],
            "translation": result["translation"],
            "pronunciation": result.get("pronunciation"),
            "source_lang": result["source_lang"],
            "target_lang": result["target_lang"],
        }

        response_serializer = TranslateResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
class PhraseViewSet(viewsets.ModelViewSet):
    """
    CRUD for user's phrases with filtering and search endpoint
    GET, POST    /api/phrases/
    GET, PUT, PATCH, DELETE /api/phrases/{id}/

    Examples:
        # List English to Spanish phrases containing "hello"
        GET /api/phrases/?source_language=en&target_language=es&search=hello
        
        # Create new phrase
        POST /api/phrases/
        {
            "original_text": "Good morning",
            "translated_text": "Buenos dias", 
            "source_language": 1,
            "target_language": 2
        }
        
        # Response
        {
            "id": 15,
            "original_text": "Good morning",
            "translated_text": "Buenos dias",
            "source_language": "en",
            "target_language": "es"
        }
    """

    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ["source_language", "target_language", "source_type"]  
    search_fields =  ["original_text", "translated_text"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
            Return only current users phrases 
        """
        return (
            Phrase.objects.filter(user=self.request.user)
            .select_related("source_language", "target_language", "user")
            .prefetch_related("categories")
        )
    
    def get_serializer_class(self):
        """
            Use different serializers for different actions.
        """
        if self.action == 'list':
            return PhraseListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return PhraseCreateSerializer
        return PhraseDetailSerializer
    
    def perform_create(self, serializer):
        """
        Auto-assign current user to new phrases.
        
    """
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
   This works for handling phrase categories 

    ENDPOINTS:
    GET /api/phrases/categories/       - List all categories (paginated)
    GET /api/phrases/categories/{id}/  - Retrieve a specific category

    AVAILABLE FILTERS:
    ?type=grammar  - Only grammar categories
    ?type=theme    - Only theme categories

    EXAMPLES:
    /api/phrases/categories/?type=grammar
    /api/phrases/categories/?page=2

    """
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["type"]
    

