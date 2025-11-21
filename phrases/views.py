from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import TranslateRequestSerializer, TranslateResponseSerializer
from .services.translation_service import TranslationService
from .models import Phrase, Language

# Create your views here.


class TranslateView(APIView):
    permission_classes = [permissions.AllowAny]   #TODO: ONLY FOR TESTING, BUT THIS IS WITH USER AUTEN

    def post(self, request):
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