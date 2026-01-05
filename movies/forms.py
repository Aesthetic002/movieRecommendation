from django import forms
from .models import Rating, UserProfile


class RatingForm(forms.Form):
    rating = forms.FloatField(
        min_value=1.0,
        max_value=5.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '1',
            'max': '5'
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
