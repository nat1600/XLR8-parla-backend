import requests
from django.conf import settings
from .base import TranslationProvider


class LibreTranslateProvider(TranslationProvider):
    """
    libreTranslate -> this dont need apikey
    """

    def __init__(self):
        self.base_url = getattr(settings, 'LIBRETRANSLATE_URL', 'https://libretranslate.com')
        self.api_key = getattr(settings, 'LIBRETRANSLATE_API_KEY', None)

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:

        url = f"{self.base_url}/translate"

        payload = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': "text"
        }

        if self.api_key:
            payload['api_key'] = self.api_key

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            return {
                'translation': data.get('translatedText', ''),
                'pronunciation': None
            }

        except requests.RequestException as e:
            raise Exception(f"error translating with LibreTranslate: {str(e)}")

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/languages", timeout=5)
            return response.status_code == 200
        except:
            return False
