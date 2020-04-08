from django.apps import AppConfig


class DjangoSimpleAccountConfig(AppConfig):
    name = 'django_simple_account'

    def ready(self):
        from django_simple_account import signals
