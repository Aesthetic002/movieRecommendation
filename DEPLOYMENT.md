# Deployment Checklist

## Pre-Deployment

### 1. Code Ready
- [ ] All C files compile without errors
- [ ] Django migrations created and tested
- [ ] All tests pass (if you have tests)
- [ ] Templates render correctly
- [ ] CSV sync works properly

### 2. Environment Configuration
- [ ] `.env.example` file created
- [ ] `.gitignore` includes sensitive files
- [ ] SECRET_KEY is secure (not the default)
- [ ] DEBUG=False in production settings

### 3. AWS S3 Setup (Optional but Recommended)
- [ ] S3 bucket created
- [ ] Bucket has public read policy
- [ ] IAM user created with S3 permissions
- [ ] Access keys saved securely

## Render Deployment Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Movie Recommendation System"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Create Render Account
- Sign up at https://render.com
- Connect GitHub account

### 3. Create PostgreSQL Database
1. Click "New" → "PostgreSQL"
2. Name: `movie-db`
3. Database: `movie_db`
4. User: `movie_user`
5. Plan: Free
6. Create Database
7. Copy **Internal Database URL** (starts with `postgres://`)

### 4. Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `movie-recommendation`
   - **Region**: Oregon (or closest to you)
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn movie_site.wsgi:application`
   - **Plan**: Free

### 5. Environment Variables
Add these in Render dashboard:

**Required:**
```
SECRET_KEY = <generate-with-django-secret-key-generator>
DEBUG = False
ALLOWED_HOSTS = <your-app-name>.onrender.com
DATABASE_URL = <paste-internal-database-url>
```

**Optional (for S3):**
```
USE_S3 = True
AWS_ACCESS_KEY_ID = <your-aws-key>
AWS_SECRET_ACCESS_KEY = <your-aws-secret>
AWS_STORAGE_BUCKET_NAME = <your-bucket-name>
AWS_S3_REGION_NAME = us-east-1
```

### 6. Deploy
1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Watch logs for errors

### 7. Post-Deployment Setup

**Via Render Shell:**
```bash
# Create superuser
python manage.py createsuperuser

# Import movies
python manage.py import_movies

# Create test user (optional)
python manage.py create_test_user
```

## Deployment Verification

### Check These Work:
- [ ] Homepage loads: `https://your-app.onrender.com/`
- [ ] Admin login: `https://your-app.onrender.com/admin/`
- [ ] User registration works
- [ ] Login works
- [ ] Movie list displays
- [ ] Can rate movies
- [ ] Recommendations work (after rating some movies)
- [ ] Static files load (Bootstrap CSS)
- [ ] Media uploads work (if using S3)

## Troubleshooting Deployment

### Build Fails
- Check build logs in Render dashboard
- Ensure `build.sh` has executable permissions
- Verify all dependencies in `requirements.txt`
- Check Python version matches `runtime.txt`

### C Engine Not Compiling
- Check build logs for gcc errors
- Ensure all .c and .h files are committed
- Verify Makefile is correct

### Static Files Not Loading
- Run: `python manage.py collectstatic`
- Check `STATIC_ROOT` in settings
- Verify WhiteNoise middleware is in `MIDDLEWARE`

### Database Connection Error
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL database is running
- Ensure `psycopg2-binary` is in requirements.txt

### Recommendations Not Working
- SSH into Render shell
- Check c_interface executable exists: `ls -la c_interface`
- Test manually: `./c_interface recommend 101 5`
- Verify CSV files exist and have data
- Run: `python manage.py sync_csv`

## Post-Deployment

### Add Content
1. Login to admin
2. Add movies with details
3. Upload movie posters
4. Create test accounts
5. Add sample ratings

### Monitor
- Check Render logs regularly
- Monitor database usage
- Watch for errors in Django logs

### Maintenance
```bash
# Sync data to CSV
python manage.py sync_csv

# Backup database (via Render dashboard)
# Render provides automatic PostgreSQL backups

# Update code
git push origin main
# Render auto-deploys
```

## Free Tier Limitations

**Render Free Plan:**
- Web service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free
- Shared resources

**PostgreSQL Free Plan:**
- 1 GB storage
- Expires after 90 days (need to migrate to paid)
- Automatic backups

**AWS S3:**
- 5 GB free for 12 months
- Pay per GB after free tier

## Upgrade Path

When ready to upgrade:
1. Render: $7/month for always-on instance
2. PostgreSQL: $7/month for persistent database
3. AWS S3: Pay-as-you-go (usually $1-5/month)

## Security Checklist

- [ ] SECRET_KEY is not in repository
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured correctly
- [ ] AWS credentials not in code
- [ ] .env file in .gitignore
- [ ] Strong admin password
- [ ] HTTPS enabled (automatic on Render)

## Performance Optimization (Optional)

- Enable Django caching
- Optimize database queries
- Compress images before upload
- Use CDN for static files
- Add database indexes

## Support Resources

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com/
- **AWS S3 Docs**: https://docs.aws.amazon.com/s3/
- **This Project**: README.md, QUICKSTART.md
