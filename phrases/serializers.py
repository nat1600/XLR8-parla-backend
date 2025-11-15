from rest_framework import serializers
from .models import Language, Category, Phrase


class LanguageSerializer(serializers.ModelSerializer):
    """
    languages serializer
    """
    class Meta:
        model = Language
        fields = ['id', 'code', 'name']


class CategorySerializer(serializers.ModelSerializer):
    """
    categories
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'type_display', 'description']


class PhraseListSerializer(serializers.ModelSerializer):
    """
    phrases
    """
    source_language = LanguageSerializer(read_only=True)
    target_language = LanguageSerializer(read_only=True)
    
    class Meta:
        model = Phrase
        fields = [
            'id',
            'original_text',
            'translated_text',
            'source_language',
            'target_language',
            'source_type',
            'created_at',
        ]


class PhraseDetailSerializer(serializers.ModelSerializer):
    """
    deratails from categories
    """
    source_language = LanguageSerializer(read_only=True)
    target_language = LanguageSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Phrase
        fields = [
            'id',
            'user',
            'original_text',
            'translated_text',
            'pronunciation',
            'source_language',
            'target_language',
            'source_url',
            'source_type',
            'context',
            'categories',
            'created_at',
            'updated_at',
        ]


class PhraseCreateSerializer(serializers.ModelSerializer):
    """
    per create phrases
    """
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Phrase
        fields = [
            'original_text',
            'translated_text',
            'pronunciation',
            'source_language',
            'target_language',
            'source_url',
            'source_type',
            'context',
            'category_ids',
        ]
    
    def create(self, validated_data):
        """create phrase wtih category"""
        category_ids = validated_data.pop('category_ids', [])
        phrase = Phrase.objects.create(**validated_data)
        
        if category_ids:
            phrase.categories.set(category_ids)
        
        return phrase


class TranslateRequestSerializer(serializers.Serializer):
    """
    traduction
    """
    text = serializers.CharField(max_length=5000)
    source_lang = serializers.CharField(max_length=10)
    target_lang = serializers.CharField(max_length=10)


class TranslateResponseSerializer(serializers.Serializer):
    """
    answer per traduction
    """
    original = serializers.CharField()
    translation = serializers.CharField()
    pronunciation = serializers.CharField(required=False, allow_null=True)
    source_lang = serializers.CharField()
    target_lang = serializers.CharField()