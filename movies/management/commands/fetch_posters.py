"""
Django management command to fetch movie posters from TMDB

Usage:
    python manage.py fetch_posters --api-key YOUR_TMDB_API_KEY
    python manage.py fetch_posters --api-key YOUR_KEY --limit 10  # Test with 10 movies
    python manage.py fetch_posters --api-key YOUR_KEY --force     # Re-download all
"""

import time
import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie


class Command(BaseCommand):
    help = 'Fetch movie posters from TMDB API'
    
    TMDB_API_BASE = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            required=True,
            help='TMDB API key (get free at themoviedb.org/settings/api)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of movies to process'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-download existing posters'
        )
    
    def search_movie(self, api_key, title, year):
        """Search TMDB for a movie"""
        url = f"{self.TMDB_API_BASE}/search/movie"
        params = {"api_key": api_key, "query": title, "year": year}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["results"][0] if data.get("results") else None
        except Exception as e:
            self.stdout.write(f"  Error: {e}")
            return None
    
    def download_poster(self, poster_path, save_path):
        """Download poster image"""
        url = f"{self.TMDB_IMAGE_BASE}{poster_path}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            self.stdout.write(f"  Error: {e}")
            return False
    
    def handle(self, *args, **options):
        api_key = options['api_key']
        limit = options.get('limit')
        force = options.get('force', False)
        
        # Create posters directory
        posters_dir = Path(settings.BASE_DIR) / 'media' / 'posters'
        posters_dir.mkdir(parents=True, exist_ok=True)
        
        movies = Movie.objects.all()
        if limit:
            movies = movies[:limit]
        
        total = movies.count()
        success = skipped = failed = 0
        
        self.stdout.write(f"\nFetching posters for {total} movies...\n")
        
        for i, movie in enumerate(movies, 1):
            self.stdout.write(f"[{i}/{total}] {movie.title} ({movie.year})")
            
            if not force and movie.poster:
                self.stdout.write("  Skipped (exists)")
                skipped += 1
                continue
            
            tmdb_movie = self.search_movie(api_key, movie.title, movie.year)
            
            if not tmdb_movie or not tmdb_movie.get("poster_path"):
                self.stdout.write("  No poster found")
                failed += 1
                continue
            
            poster_filename = f"{movie.movie_id}.jpg"
            save_path = posters_dir / poster_filename
            
            if self.download_poster(tmdb_movie["poster_path"], save_path):
                movie.poster = f"posters/{poster_filename}"
                movie.save()
                self.stdout.write(self.style.SUCCESS("  ✓ Downloaded"))
                success += 1
            else:
                failed += 1
            
            time.sleep(0.3)  # Rate limiting
        
        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {success} downloaded, {skipped} skipped, {failed} failed"
        ))
