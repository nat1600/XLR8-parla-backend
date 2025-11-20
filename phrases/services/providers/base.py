from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    """
    abstract class for translate providers
    """

    @abstractmethod
    def translate(self, text:str, source_lang:str, target_lang:str)-> dict:
        """
        translate text

        this is going to return:
        dict:{
        'translation': str
        'pronunciation'str, it maybe optional
        }
        """


        pass


    @abstractmethod
    
    def is_avaible(self) -> bool:
        """
        Is avaible the provider
        """
        pass

