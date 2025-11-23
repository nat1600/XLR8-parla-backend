import requests
from django.conf import settings
from .base import TranslationProvider


class DeepLProvider(TranslationProvider):
    """
    DeepL API FREE – 500k chars/month
    """

    def __init__(self):
        self.api_key = getattr(settings, 'DEEPL_API_KEY', None)
        self.base_url = "https://api-free.deepl.com/v2"

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:

        if not self.api_key:
            raise Exception('DeepL API key not configured')

        url = f"{self.base_url}/translate"

        headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}"
        }

        payload = {
            "text": text,
            "target_lang": target_lang.upper()
        }

        if source_lang:
            payload["source_lang"] = source_lang.upper()

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            return {
                "translation": data["translations"][0]["text"],
                "pronunciation": None
            }

        except requests.HTTPError as http_err:
            ## quota
            if hasattr(http_err.response, "status_code") and http_err.response.status_code == 456:
                raise Exception("DeepL FREE quota exceeded (500k/month)")
            raise Exception(f"DeepL HTTP error: {http_err}")

        except Exception as e:
            raise Exception(f"DeepL error: {str(e)}")

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            url = f"{self.base_url}/usage"
            headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                used = data.get("character_count", 0)
                limit = data.get("character_limit", 500000)
                return used < limit
            return False
        except:
            return False
