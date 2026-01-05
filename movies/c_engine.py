"""
C Engine Integration - Minimal wrapper using subprocess
Calls c_interface executable and parses JSON output
"""
import subprocess
import json
import csv
import os
from pathlib import Path
from django.conf import settings


class CRecommendationEngine:
    """Wrapper for C recommendation engine"""
    
    def __init__(self):
        self.base_dir = Path(settings.BASE_DIR)
        self.executable = self.base_dir / 'c_interface'
        if os.name == 'nt':  # Windows
            self.executable = self.base_dir / 'c_interface.exe'
    
    def get_recommendations(self, user_id, count=10):
        """
        Get movie recommendations for a user
        Returns: list of dicts with movie info and predicted rating
        """
        try:
            result = subprocess.run(
                [str(self.executable), 'recommend', str(user_id), str(count)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"C engine error: {result.stderr}")
            
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse C engine output: {e}")
        except Exception as e:
            raise Exception(f"Recommendation engine error: {e}")
    
    def add_rating(self, user_id, movie_id, rating):
        """
        Add a rating via C engine (updates CSV)
        Returns: True on success
        """
        try:
            result = subprocess.run(
                [str(self.executable), 'add_rating', str(user_id), str(movie_id), str(rating)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise Exception(f"C engine error: {result.stderr}")
            
            # Debug: print what we got
            if not result.stdout.strip():
                raise Exception(f"C engine returned empty output. stderr: {result.stderr}")
            
            response = json.loads(result.stdout)
            return response.get('status') == 'success'
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON from C engine. stdout: '{result.stdout}', stderr: '{result.stderr}'")
        except Exception as e:
            raise Exception(f"Add rating error: {e}")


class CSVSync:
    """Sync Django models with C engine CSV files"""
    
    @staticmethod
    def export_movies():
        """Export movies from Django to CSV"""
        from movies.models import Movie
        
        csv_path = Path(settings.BASE_DIR) / 'movies.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['movie_id', 'title', 'genre', 'year'])
            
            for movie in Movie.objects.all():
                writer.writerow([movie.movie_id, movie.title, movie.genre, movie.year])
    
    @staticmethod
    def export_users():
        """Export users from Django to CSV"""
        from movies.models import UserProfile
        
        csv_path = Path(settings.BASE_DIR) / 'users.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'name', 'age'])
            
            for profile in UserProfile.objects.select_related('user').all():
                writer.writerow([profile.c_user_id, profile.user.username, profile.age])
    
    @staticmethod
    def export_ratings():
        """Export ratings from Django to CSV"""
        from movies.models import Rating
        
        csv_path = Path(settings.BASE_DIR) / 'ratings.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'movie_id', 'rating'])
            
            for rating in Rating.objects.select_related('user__profile', 'movie').all():
                try:
                    user_id = rating.user.profile.c_user_id
                    movie_id = rating.movie.movie_id
                    writer.writerow([user_id, movie_id, rating.rating])
                except:
                    pass  # Skip if profile doesn't exist
    
    @staticmethod
    def import_movies():
        """Import movies from CSV to Django"""
        from movies.models import Movie
        
        csv_path = Path(settings.BASE_DIR) / 'movies.csv'
        if not csv_path.exists():
            return
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Movie.objects.update_or_create(
                    movie_id=int(row['movie_id']),
                    defaults={
                        'title': row['title'],
                        'genre': row['genre'],
                        'year': int(row['year'])
                    }
                )
    
    @staticmethod
    def sync_all():
        """Full bidirectional sync"""
        CSVSync.export_movies()
        CSVSync.export_users()
        CSVSync.export_ratings()
