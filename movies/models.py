from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Movie(models.Model):
    """Movie model - syncs with C engine via CSV"""
    movie_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    year = models.IntegerField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    avg_rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} ({self.year})"


class UserProfile(models.Model):
    """Extended user profile - syncs with C engine via CSV"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    c_user_id = models.IntegerField(unique=True, db_index=True)  # ID for C engine
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    ratings_count = models.IntegerField(default=0)
    avg_rating_given = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.user.username} (ID: {self.c_user_id})"


class Rating(models.Model):
    """Rating model - syncs with C engine via CSV"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}"
