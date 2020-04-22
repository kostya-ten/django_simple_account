import importlib

from django.apps import AppConfig


class DjangoSimpleAccountConfig(AppConfig):
    name = 'django_simple_account'
    verbose_name = "Django simple account"

    def ready(self):
        importlib.import_module('django_simple_account.signals')
