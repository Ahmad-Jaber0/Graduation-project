from django.apps import AppConfig
from suit.apps import DjangoSuitConfig

class HierarchyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hierarchy'

class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'