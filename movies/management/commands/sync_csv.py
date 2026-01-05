"""
Management command to sync Django data to CSV files for C engine
"""
from django.core.management.base import BaseCommand
from movies.c_engine import CSVSync


class Command(BaseCommand):
    help = 'Sync Django models to CSV files for C recommendation engine'

    def handle(self, *args, **options):
        self.stdout.write('Syncing data to CSV files...')
        
        try:
            CSVSync.sync_all()
            self.stdout.write(self.style.SUCCESS('Successfully synced all data to CSV files'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error syncing data: {e}'))
