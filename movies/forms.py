from django import forms
from .models import Rating, UserProfile


class RatingForm(forms.Form):
    RATING_CHOICES = [
        (1, '⭐ 1 - Poor'),
        (2, '⭐⭐ 2 - Fair'),
        (3, '⭐⭐⭐ 3 - Good'),
        (4, '⭐⭐⭐⭐ 4 - Very Good'),
        (5, '⭐⭐⭐⭐⭐ 5 - Excellent'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Your Rating (1-5)'
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'})
        }
