
import requests
from .base import TranslationProvider


class MyMemoryProvider(TranslationProvider):
    """
    MyMemory API
    https://mymemory.translated.net/doc/spec.php
    """

    def __init__(self):
        self.base_url = "https://api.mymemory.translated.net"

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        url = f"{self.base_url}/get"
        params = {
            'q': text,
            'langpair': f'{source_lang}|{target_lang}'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('responseStatus') != 200:
                raise Exception("Error en MyMemory response")

            return {
                'translation': data['responseData']['translatedText'],
                'pronunciation': None
            }

        except requests.RequestException as e:
            raise Exception(f"Error translating with MyMemory: {str(e)}")

    def is_available(self) -> bool:
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code in [200, 404]
        except:
            return False
