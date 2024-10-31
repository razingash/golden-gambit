from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "data reinitialization"

    def handle(self, *args, **options):
        call_command('deinitialization')
        call_command('initialization')
