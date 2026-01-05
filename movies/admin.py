from django.contrib import admin
from django.utils.html import format_html
from .models import Movie, UserProfile, Rating


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('movie_id', 'title', 'genre', 'year', 'avg_rating', 'rating_count', 'poster_preview')
    list_filter = ('genre', 'year')
    search_fields = ('title', 'genre')
    ordering = ('title',)
    
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="50" height="75" />', obj.poster.url)
        return "No poster"
    poster_preview.short_description = 'Poster'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('c_user_id', 'user', 'age', 'ratings_count', 'avg_rating_given')
    search_fields = ('user__username', 'user__email')
    ordering = ('c_user_id',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'movie__title')
    ordering = ('-created_at',)
