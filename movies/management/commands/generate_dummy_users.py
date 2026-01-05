"""
Management command to generate dummy users with random ratings
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Max
from movies.models import UserProfile, Movie, Rating
from movies.c_engine import CSVSync
import random


class Command(BaseCommand):
    help = 'Generate dummy users with random ratings for testing recommendations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of dummy users to create (default: 50)'
        )
        parser.add_argument(
            '--min-ratings',
            type=int,
            default=5,
            help='Minimum ratings per user (default: 5)'
        )
        parser.add_argument(
            '--max-ratings',
            type=int,
            default=20,
            help='Maximum ratings per user (default: 20)'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        min_ratings = options['min_ratings']
        max_ratings = options['max_ratings']
        
        self.stdout.write(f'Generating {num_users} dummy users...')
        
        # Get all movies
        movies = list(Movie.objects.all())
        if not movies:
            self.stdout.write(self.style.ERROR('No movies found! Import movies first.'))
            return
        
        self.stdout.write(f'Found {len(movies)} movies')
        
        # Get current max c_user_id
        max_id = UserProfile.objects.aggregate(max_id=Max('c_user_id'))['max_id']
        next_user_id = (max_id or 100) + 1
        
        first_names = [
            'John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa',
            'Tom', 'Anna', 'James', 'Mary', 'Robert', 'Patricia', 'Michael',
            'Jennifer', 'William', 'Linda', 'Richard', 'Barbara', 'Joseph',
            'Elizabeth', 'Thomas', 'Susan', 'Charles', 'Jessica', 'Daniel',
            'Karen', 'Matthew', 'Nancy', 'Anthony', 'Betty', 'Mark', 'Helen',
            'Donald', 'Sandra', 'Steven', 'Donna', 'Paul', 'Carol', 'Andrew',
            'Ruth', 'Joshua', 'Sharon', 'Kenneth', 'Michelle', 'Kevin', 'Laura'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Thompson', 'White', 'Harris', 'Clark', 'Lewis', 'Robinson',
            'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres',
            'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker'
        ]
        
        created_count = 0
        rating_count = 0
        
        for i in range(num_users):
            # Generate username
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            
            # Check if username exists
            if User.objects.filter(username=username).exists():
                username = f"{username}{random.randint(1000, 9999)}"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password='dummypass123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            age = random.randint(18, 65)
            profile = UserProfile.objects.create(
                user=user,
                c_user_id=next_user_id,
                age=age
            )
            next_user_id += 1
            created_count += 1
            
            # Generate random ratings
            num_ratings = random.randint(min_ratings, max_ratings)
            rated_movies = random.sample(movies, min(num_ratings, len(movies)))
            
            for movie in rated_movies:
                # Realistic rating distribution (skewed toward higher ratings)
                rating_value = random.choices(
                    [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                    weights=[1, 1, 2, 3, 8, 12, 20, 25, 28]
                )[0]
                
                Rating.objects.create(
                    user=user,
                    movie=movie,
                    rating=rating_value
                )
                rating_count += 1
            
            # Update profile stats
            user_ratings = Rating.objects.filter(user=user)
            profile.ratings_count = user_ratings.count()
            if profile.ratings_count > 0:
                profile.avg_rating_given = sum(r.rating for r in user_ratings) / profile.ratings_count
            profile.save()
            
            # Update movie stats
            for movie in rated_movies:
                movie_ratings = Rating.objects.filter(movie=movie)
                movie.rating_count = movie_ratings.count()
                if movie.rating_count > 0:
                    movie.avg_rating = sum(r.rating for r in movie_ratings) / movie.rating_count
                movie.save()
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Created {i + 1}/{num_users} users...')
        
        # Sync to CSV files for C engine
        self.stdout.write('Syncing data to CSV files...')
        CSVSync.sync_all()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully created {created_count} dummy users'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✓ Generated {rating_count} ratings'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✓ Average ratings per user: {rating_count / created_count:.1f}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✓ Data synced to CSV files for C recommendation engine'
        ))
        self.stdout.write('\nRecommendations should now work properly!')
