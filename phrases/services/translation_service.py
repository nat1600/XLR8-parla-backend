from .providers.deepl import DeepLProvider
from .providers.libretranslate import LibreTranslateProvider
from .providers.mymemory import MyMemoryProvider


class TranslationService:
    """
    This is useful for allow multiple providers
    https://docs.libretranslate.com/
    """

    def __init__(self):
        self.providers = [
            DeepLProvider(),
            LibreTranslateProvider(),
            MyMemoryProvider(),
        ]

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        errors = []

        for provider in self.providers:
            try:
                #  check if provider is available
                if not provider.is_available():
                    errors.append(f"{provider.__class__.__name__}: Not avaiblable")
                    continue

                # try translation
                result = provider.translate(text, source_lang, target_lang)

                return {
                    'original': text,
                    'translation': result['translation'],
                    'pronunciation': result.get('pronunciation'),
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'provider': provider.__class__.__name__,
                }

            except Exception as e:
                errors.append(
                    f"{provider.__class__.__name__}: {str(e)}"
                )
                continue

        # if all providers failed
        error_msg = "All providers failed:\n" + "\n".join(errors)
        raise Exception(error_msg)
