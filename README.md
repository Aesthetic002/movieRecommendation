# Movie Recommendation Website

A movie recommendation system built with Django frontend and C-based collaborative filtering backend. The project wraps an existing C recommendation engine with a minimal Django web interface.

## Architecture

- **Backend**: Django 5.0
- **Core Algorithm**: C (existing recommendation engine)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Storage**: Amazon S3 (movie posters)
- **Deployment**: Render

## Project Structure

```
DSA EL/
├── c_interface.c          # CLI wrapper for C engine (minimal changes)
├── main.c                 # Original C program (preserved)
├── file_io.c/h            # C modules (unchanged)
├── graph.c/h
├── hash_table.c/h
├── movie.c/h
├── recommendation.c/h
├── user.c/h
├── Makefile               # Compiles C code
│
├── movie_site/            # Django project
│   ├── settings.py        # S3, PostgreSQL config
│   └── urls.py
│
├── movies/                # Django app
│   ├── models.py          # Movie, User, Rating models
│   ├── views.py           # Web views
│   ├── c_engine.py        # Python wrapper for C subprocess
│   ├── admin.py           # Django admin config
│   ├── forms.py
│   └── templates/
│
├── movies.csv             # C engine data files
├── users.csv
├── ratings.csv
│
└── build.sh               # Render build script
```

## Features

### User Features
- User registration and authentication
- Browse movies with search and filters
- Rate movies (1-5 stars)
- Get personalized recommendations (powered by C algorithm)
- View rating history

### Admin Features (Django Admin)
- Add/edit/delete movies
- Upload movie posters (stored on S3)
- View users and ratings
- Manage all database content

## How It Works

1. **Django handles**: Web UI, authentication, database management
2. **C engine handles**: Recommendation algorithm (collaborative filtering)
3. **Integration**: 
   - Django writes data to CSV files
   - Calls compiled C executable via subprocess
   - Parses JSON output from C program
   - No algorithm changes to C code

## Setup Instructions

### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Compile C Engine**
```bash
make c_interface
```

3. **Setup Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run Migrations**
```bash
python manage.py migrate
```

5. **Import Initial Data**
```bash
python manage.py shell
>>> from movies.c_engine import CSVSync
>>> CSVSync.import_movies()
>>> exit()
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

Visit http://localhost:8000

### Adding Movies via Admin

1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Click "Movies" → "Add Movie"
4. Fill in: movie_id, title, genre, year
5. Upload poster image (optional)
6. Save

### Production Deployment (Render)

1. **Prerequisites**
   - GitHub repository
   - Render account
   - AWS S3 bucket for posters
   - PostgreSQL database (provided by Render)

2. **Environment Variables on Render**
   ```
   SECRET_KEY=<generate-random-key>
   DEBUG=False
   ALLOWED_HOSTS=<your-render-url>.onrender.com
   DATABASE_URL=<auto-filled-by-render>
   USE_S3=True
   AWS_ACCESS_KEY_ID=<your-aws-key>
   AWS_SECRET_ACCESS_KEY=<your-aws-secret>
   AWS_STORAGE_BUCKET_NAME=<your-bucket-name>
   AWS_S3_REGION_NAME=us-east-1
   ```

3. **Deploy Steps**
   - Connect GitHub repo to Render
   - Select "Web Service"
   - Build Command: `./build.sh`
   - Start Command: `gunicorn movie_site.wsgi:application`
   - Add PostgreSQL database
   - Set environment variables
   - Deploy

4. **Post-Deployment**
   ```bash
   # Create superuser via Render shell
   python manage.py createsuperuser
   
   # Sync CSV data
   python manage.py sync_csv
   ```

## AWS S3 Setup

1. Create S3 bucket
2. Set bucket policy for public read access:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

3. Create IAM user with S3 permissions
4. Add credentials to environment variables

## C Engine Integration

The C recommendation engine is called via subprocess:

```python
# Get recommendations
engine = CRecommendationEngine()
recommendations = engine.get_recommendations(user_id=101, count=10)

# Add rating
engine.add_rating(user_id=101, movie_id=5, rating=4.5)
```

**Data Flow:**
1. Django models → CSV files (movies.csv, users.csv, ratings.csv)
2. C program reads CSV files
3. C program generates recommendations
4. C program outputs JSON
5. Django parses JSON and displays results

## Management Commands

```bash
# Sync Django data to CSV files
python manage.py sync_csv

# Standard Django commands
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## Testing the C Engine Directly

```bash
# Compile
make c_interface

# Get recommendations for user 101
./c_interface recommend 101 10

# Add rating
./c_interface add_rating 101 5 4.5
```

## API Endpoints

- `/` - Home page
- `/movies/` - Movie list with search
- `/movies/<id>/` - Movie detail and rating form
- `/recommendations/` - Personalized recommendations
- `/my-ratings/` - User's rating history
- `/register/` - User registration
- `/login/` - Login
- `/admin/` - Django admin panel

## Database Schema

### Movie
- movie_id (unique identifier for C engine)
- title
- genre
- year
- poster (S3 URL)
- avg_rating
- rating_count

### UserProfile
- user (OneToOne with Django User)
- user_id (unique identifier for C engine)
- age
- ratings_count
- avg_rating_given

### Rating
- user (ForeignKey)
- movie (ForeignKey)
- rating (1.0-5.0)
- created_at
- updated_at

## Technology Stack

- **Python 3.11**
- **Django 5.0**
- **PostgreSQL** (production database)
- **SQLite** (development database)
- **C** (recommendation algorithm)
- **Gunicorn** (WSGI server)
- **WhiteNoise** (static file serving)
- **Boto3** (AWS S3 integration)
- **Bootstrap 5** (frontend styling)

## Design Philosophy

✅ **Minimal Changes**: C code treated as black box  
✅ **Simple Integration**: Subprocess calls, CSV I/O  
✅ **No Refactoring**: Original algorithm preserved  
✅ **Thin Wrapper**: Django only handles web layer  

## Troubleshooting

**C engine not compiling**
- Ensure gcc is installed
- Check Makefile paths
- On Windows, use MinGW or WSL

**Recommendations not working**
- Check CSV files exist
- Run `python manage.py sync_csv`
- Verify c_interface executable exists
- Check user has profile with user_id

**S3 uploads failing**
- Verify AWS credentials
- Check bucket permissions
- Ensure USE_S3=True in environment

## License

This project wraps an existing C recommendation engine with minimal modifications.

## Support

For issues related to:
- Django/Web: Check Django documentation
- C Engine: Review original C code documentation
- Deployment: Check Render.com docs
- AWS S3: Check AWS documentation
