from django.db import models
from django.conf import settings

# Create your models here.


class Language(models.Model):
    code = models.CharField(max_length=10, unique = True)
    name = models.CharField(max_length=50)

    ## this works for the table name instead of show appname_modelname this is going to show 'Languages'
    class Meta:
        db_table = 'languages'

    def __str__(self):
        """
        This is a magic method in python for define how an object can be represented like a text
        """
        return self.name
    
class Category (models.Model):
    CATEGORY_TYPES = [
        ('grammar', 'Gramática'),
        ('theme', 'Temática'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_lenght = 20, choices = CATEGORY_TYPES)
    description = models.TextField (null=True, blank =True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class Pharse(models.Model):
    SOURCE_TYPES =[
        ('youtube','Youtube'),
        ('netflix', 'Netflix'),
        ('web', 'Wen'),
        ('pdf', 'PDF'), # i dont know if we are going to left this, so we have to review this
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='phrases')
    original_text = models.TextField()
    translated_text = models.TextField()
    pronunciation = models.TextField(null=True, blank=True)
    source_language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='source_phrases')
    target_language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='target_phrases')
    source_url = models.URLField(null=True, blank=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='phrases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'phrases'
        ordering =  ['-created_at']