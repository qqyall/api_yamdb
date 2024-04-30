import csv

from django.core.management.base import BaseCommand
from users.models import MyUser


class Command(BaseCommand):
    help = 'Loads users from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
                            help='The CSV file to load users from')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to import users...'))
        self.import_users(options['csv_file'])

    def import_users(self, csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            users_created = 0
            for row in reader:
                _, created = MyUser.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        'bio': row['bio'] if row['bio'] else '',
                        'first_name':
                        row['first_name'] if row['first_name'] else '',
                        'last_name':
                        row['last_name'] if row['last_name'] else ''
                    }
                )
                if created:
                    users_created += 1
            self.stdout.write(self.style.SUCCESS(
                f'{users_created} users imported successfully!'))
