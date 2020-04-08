from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def handle(self, *args, **options):
        options['ignore_patterns'].append('venv')
        super().handle(*args, **options)
