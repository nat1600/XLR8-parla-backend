from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    """
    abstract class for translate providers
    """

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """
        Must return a dict:
        {
            'translation': str,
            'pronunciation': str | None
        }
        """
        pass


    @abstractmethod
    
    def is_available(self) -> bool:
        """
        Is avaible the provider
        """
        pass

