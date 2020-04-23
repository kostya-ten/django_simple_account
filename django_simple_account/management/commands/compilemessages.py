from django.core.management.commands import compilemessages


class Command(compilemessages.Command):
    def handle(self, **options):
        options['ignore_patterns'].append('venv')
        super().handle(**options)
