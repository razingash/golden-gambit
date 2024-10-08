from django.core.management import BaseCommand, call_command


class Command(BaseCommand): # mb change file name to another one
    help = "initialization command, run this command once"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Initialization...'))

        call_command('makemigrations')
        call_command('migrate')
        call_command('generate_static_data')
        call_command('generate_random_data')

        self.stdout.write(self.style.SUCCESS('Initialization completed'))
