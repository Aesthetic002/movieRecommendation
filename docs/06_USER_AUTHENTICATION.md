# User Authentication & Profile System

## Overview

The authentication system combines Django's built-in auth with custom user profiles that sync with the C engine.

---

## Models

### Django User (Built-in)
Standard Django User model with username, password, email.

### UserProfile (Custom)

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='profile')
    c_user_id = models.IntegerField(unique=True, db_index=True)
    age = models.IntegerField(validators=[MinValueValidator(1), 
                                          MaxValueValidator(120)])
    ratings_count = models.IntegerField(default=0)
    avg_rating_given = models.FloatField(default=0.0)
```

**Fields:**
| Field | Description |
|-------|-------------|
| `user` | OneToOne link to Django User |
| `c_user_id` | Unique ID for C engine (starts at 101) |
| `age` | User's age (1-120) |
| `ratings_count` | Number of ratings given |
| `avg_rating_given` | Average of all ratings |

---

## Registration Flow

```python
def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # Generate unique c_user_id
            max_id = UserProfile.objects.aggregate(
                max_id=Max('c_user_id'))['max_id']
            profile.c_user_id = (max_id or 100) + 1
            profile.save()
            
            CSVSync.export_users()  # Sync to C engine
            login(request, user)
            return redirect('home')
```

---

## Authentication URLs

| URL | View | Description |
|-----|------|-------------|
| `/accounts/login/` | Django built-in | Login page |
| `/accounts/logout/` | Django built-in | Logout action |
| `/register/` | Custom | Registration with profile |
| `/complete-profile/` | Custom | Missing profile completion |

---

## Protected Views

```python
from django.contrib.auth.decorators import login_required

@login_required
def recommendations(request):
    # Only authenticated users can access
    ...

@login_required  
def my_ratings(request):
    # User's personal rating history
    ...
```

---

## Settings

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
```

---

## Profile Access

```python
# Check if user has profile
if hasattr(request.user, 'profile'):
    user_id = request.user.profile.c_user_id
else:
    return redirect('complete_profile')
```
