"""
Management command to import movies from CSV
"""
from django.core.management.base import BaseCommand
from movies.c_engine import CSVSync


class Command(BaseCommand):
    help = 'Import movies from movies.csv into Django database'

    def handle(self, *args, **options):
        self.stdout.write('Importing movies from CSV...')
        
        try:
            CSVSync.import_movies()
            self.stdout.write(self.style.SUCCESS('Successfully imported movies from CSV'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing movies: {e}'))
