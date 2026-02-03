"""
Django management command to set poster paths for existing poster files.
Use this on production (Render) after deploying the poster files.

Usage:
    python manage.py set_poster_paths
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie


class Command(BaseCommand):
    help = 'Set poster paths for movies that have poster files on disk'
    
    def handle(self, *args, **options):
        posters_dir = Path(settings.MEDIA_ROOT) / 'posters'
        
        if not posters_dir.exists():
            self.stdout.write(self.style.ERROR(f"Posters directory not found: {posters_dir}"))
            return
        
        # Get all poster files
        poster_files = set()
        for f in posters_dir.iterdir():
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                # Extract movie_id from filename (e.g., "28.jpg" -> 28)
                try:
                    movie_id = int(f.stem)
                    poster_files.add(movie_id)
                except ValueError:
                    pass
        
        self.stdout.write(f"Found {len(poster_files)} poster files on disk")
        
        updated = 0
        for movie in Movie.objects.all():
            if movie.movie_id in poster_files:
                poster_path = f"posters/{movie.movie_id}.jpg"
                if not movie.poster or str(movie.poster) != poster_path:
                    movie.poster = poster_path
                    movie.save()
                    updated += 1
                    self.stdout.write(f"  Set poster for: {movie.title}")
        
        self.stdout.write(self.style.SUCCESS(f"\nUpdated {updated} movies with poster paths"))
