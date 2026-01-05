from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q, Max
from .models import Movie, Rating, UserProfile
from .c_engine import CRecommendationEngine, CSVSync
from .forms import RatingForm, UserProfileForm


def home(request):
    """Landing page"""
    movies = Movie.objects.all()[:10]
    return render(request, 'movies/home.html', {'movies': movies})


def movie_list(request):
    """Display all movies with search"""
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    
    movies = Movie.objects.all()
    
    if query:
        movies = movies.filter(
            Q(title__icontains=query) | Q(genre__icontains=query)
        )
    
    if genre:
        movies = movies.filter(genre=genre)
    
    genres = Movie.objects.values_list('genre', flat=True).distinct()
    
    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': genres,
        'query': query,
        'selected_genre': genre
    })


def movie_detail(request, movie_id):
    """Movie detail and rating submission"""
    movie = get_object_or_404(Movie, movie_id=movie_id)
    user_rating = None
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, movie=movie).first()
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']
            
            # Update or create rating in Django
            rating_obj, created = Rating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating_value}
            )
            
            # Sync to CSV and call C engine
            try:
                CSVSync.sync_all()
                engine = CRecommendationEngine()
                engine.add_rating(
                    request.user.profile.c_user_id,
                    movie.movie_id,
                    rating_value
                )
                messages.success(request, 'Rating submitted successfully!')
            except Exception as e:
                messages.error(request, f'Error syncing rating: {e}')
            
            return redirect('movie_detail', movie_id=movie_id)
    else:
        initial_rating = user_rating.rating if user_rating else None
        form = RatingForm(initial={'rating': initial_rating})
    
    recent_ratings = Rating.objects.filter(movie=movie).select_related('user')[:5]
    
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'form': form,
        'user_rating': user_rating,
        'recent_ratings': recent_ratings
    })


@login_required
def recommendations(request):
    """Get personalized recommendations from C engine"""
    try:
        # Ensure user has profile
        if not hasattr(request.user, 'profile'):
            messages.warning(request, 'Please complete your profile first.')
            return redirect('complete_profile')
        
        # Sync data to CSV
        CSVSync.sync_all()
        
        # Call C engine
        engine = CRecommendationEngine()
        recommended_movies = engine.get_recommendations(
            request.user.profile.c_user_id,
            count=10
        )
        
        # Enrich with Django model data
        for rec in recommended_movies:
            try:
                movie = Movie.objects.get(movie_id=rec['movie_id'])
                rec['movie_obj'] = movie
            except Movie.DoesNotExist:
                pass
        
        return render(request, 'movies/recommendations.html', {
            'recommendations': recommended_movies
        })
        
    except Exception as e:
        messages.error(request, f'Error generating recommendations: {e}')
        return render(request, 'movies/recommendations.html', {
            'recommendations': [],
            'error': str(e)
        })


@login_required
def my_ratings(request):
    """Display user's ratings"""
    ratings = Rating.objects.filter(user=request.user).select_related('movie')
    return render(request, 'movies/my_ratings.html', {'ratings': ratings})


def register(request):
    """User registration with profile creation"""
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Create profile with auto-generated user_id
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # Generate c_user_id (simple: max + 1)
            max_id = UserProfile.objects.aggregate(max_id=Max('c_user_id'))['max_id']
            profile.c_user_id = (max_id or 100) + 1
            profile.save()
            
            # Sync to CSV
            CSVSync.export_users()
            
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def complete_profile(request):
    """Complete user profile if missing"""
    if hasattr(request.user, 'profile'):
        return redirect('home')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            
            # Generate c_user_id
            max_id = UserProfile.objects.aggregate(max_id=Max('c_user_id'))['max_id']
            profile.c_user_id = (max_id or 100) + 1
            profile.save()
            
            CSVSync.export_users()
            messages.success(request, 'Profile completed!')
            return redirect('home')
    else:
        form = UserProfileForm()
    
    return render(request, 'movies/complete_profile.html', {'form': form})
