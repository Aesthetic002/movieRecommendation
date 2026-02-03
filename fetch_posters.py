"""
TMDB Movie Poster Fetcher
Downloads movie posters from The Movie Database API

To use:
1. Get a free API key from https://www.themoviedb.org/settings/api
2. Run: python fetch_posters.py --api-key YOUR_API_KEY

This script will:
- Read movies from the database
- Search TMDB for each movie
- Download posters to media/posters/
- Update Django database with poster paths
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path

# Add Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_site.settings')

import django
django.setup()

from movies.models import Movie


TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def search_movie(api_key, title, year):
    """Search TMDB for a movie by title and year"""
    url = f"{TMDB_API_BASE}/search/movie"
    params = {
        "api_key": api_key,
        "query": title,
        "year": year
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            return data["results"][0]  # Return first match
        return None
    except Exception as e:
        print(f"  Error searching for {title}: {e}")
        return None


def download_poster(poster_path, save_path):
    """Download poster image from TMDB"""
    url = f"{TMDB_IMAGE_BASE}{poster_path}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"  Error downloading poster: {e}")
        return False


def fetch_all_posters(api_key, limit=None, skip_existing=True):
    """Fetch posters for all movies in database"""
    
    # Create posters directory
    posters_dir = Path("media/posters")
    posters_dir.mkdir(parents=True, exist_ok=True)
    
    movies = Movie.objects.all()
    if limit:
        movies = movies[:limit]
    
    total = movies.count()
    success = 0
    skipped = 0
    failed = 0
    
    print(f"\nFetching posters for {total} movies...")
    print("=" * 50)
    
    for i, movie in enumerate(movies, 1):
        print(f"\n[{i}/{total}] {movie.title} ({movie.year})")
        
        # Skip if poster already exists
        if skip_existing and movie.poster:
            print(f"  Skipping - poster already exists")
            skipped += 1
            continue
        
        # Search TMDB
        tmdb_movie = search_movie(api_key, movie.title, movie.year)
        
        if not tmdb_movie or not tmdb_movie.get("poster_path"):
            print(f"  No poster found on TMDB")
            failed += 1
            continue
        
        # Download poster
        poster_filename = f"{movie.movie_id}.jpg"
        save_path = posters_dir / poster_filename
        
        if download_poster(tmdb_movie["poster_path"], save_path):
            # Update Django model
            movie.poster = f"posters/{poster_filename}"
            movie.save()
            print(f"  ✓ Downloaded and saved poster")
            success += 1
        else:
            failed += 1
        
        # Rate limiting - TMDB allows 40 requests per 10 seconds
        time.sleep(0.3)
    
    print("\n" + "=" * 50)
    print(f"COMPLETE: {success} downloaded, {skipped} skipped, {failed} failed")
    print(f"\nPosters saved to: {posters_dir.absolute()}")
    print("\nRun 'python manage.py collectstatic' to update static files")


def main():
    parser = argparse.ArgumentParser(description="Fetch movie posters from TMDB")
    parser.add_argument("--api-key", required=True, help="TMDB API key")
    parser.add_argument("--limit", type=int, help="Limit number of movies to process")
    parser.add_argument("--force", action="store_true", help="Re-download existing posters")
    
    args = parser.parse_args()
    
    fetch_all_posters(
        api_key=args.api_key,
        limit=args.limit,
        skip_existing=not args.force
    )


if __name__ == "__main__":
    main()
