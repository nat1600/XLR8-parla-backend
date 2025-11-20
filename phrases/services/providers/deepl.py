import requests
from django.conf import settings
from .base import TranslationProvider


class DeepLProvider(TranslationProvider):
    """
    deepl api FREE, this is goint to give ud 500k 
    """

    def __init__(self):
        self.api_key = getattr(settings, 'DEEPL_API_KEY', None)
        self.base_url = "https://api-free.deepl.com/v2"


    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        '''
        transalte using deepl API
        '''

        if not self.api_key:
            raise Exception('api key not configured')

        url = f"{self.base_url}/translate"

        headers = {
            'Authorization': f'DeepL-Auth-Key {self.api_key}'
        }

        payload = {

            'text': [text],
            'source_lang': source_lang.upper(),
            'target_lang': target_lang.upper(),
            ## is upper cause deepl needs EN instead of en
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'translation': data['translations'][0]['text'],
                'pronunciation': None  
            }
        

        except requests.RequestException as e:
            if response.status_code == 456:
                raise Exception("Cuota de DeepL excedida (500k caracteres/mes)")
            raise Exception(f"Error al traducir con DeepL: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Verify if deepl is available and has a quota
        """
        if not self.api_key:
            return False
        
        try:
            url = f"{self.base_url}/usage"
            headers = {'Authorization': f'DeepL-Auth-Key {self.api_key}'}
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # Verify if not exceed the limit
                used = data.get('character_count', 0)
                limit = data.get('character_limit', 500000)
                return used < limit
            
            return False
        except:
            return False