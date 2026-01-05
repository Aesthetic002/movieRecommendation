"""
Management command to create a test user with sample ratings
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Max
from movies.models import UserProfile, Movie, Rating
from movies.c_engine import CSVSync
import random


class Command(BaseCommand):
    help = 'Create test user with sample ratings'

    def handle(self, *args, **options):
        self.stdout.write('Creating test user...')
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created user: testuser'))
        else:
            self.stdout.write('User testuser already exists')
        
        # Create profile if doesn't exist
        if not hasattr(user, 'profile'):
            max_id = UserProfile.objects.aggregate(max_id=Max('c_user_id'))['max_id']
            profile = UserProfile.objects.create(
                user=user,
                c_user_id=(max_id or 100) + 1,
                age=25
            )
            self.stdout.write(self.style.SUCCESS(f'Created profile with c_user_id: {profile.c_user_id}'))
        else:
            profile = user.profile
            self.stdout.write(f'Profile already exists with c_user_id: {profile.c_user_id}')
        
        # Add sample ratings
        movies = Movie.objects.all()[:10]
        if movies:
            for movie in movies:
                rating_value = round(random.uniform(3.0, 5.0), 1)
                rating, created = Rating.objects.get_or_create(
                    user=user,
                    movie=movie,
                    defaults={'rating': rating_value}
                )
                if created:
                    self.stdout.write(f'Rated {movie.title}: {rating_value}')
            
            # Sync to CSV
            CSVSync.sync_all()
            self.stdout.write(self.style.SUCCESS('Synced ratings to CSV'))
        else:
            self.stdout.write(self.style.WARNING('No movies found. Import movies first.'))
        
        self.stdout.write(self.style.SUCCESS('\nTest user ready!'))
        self.stdout.write('Username: testuser')
        self.stdout.write('Password: testpass123')
