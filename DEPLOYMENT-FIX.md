# MDCAN BDM 2025 - Digital Ocean Deployment Fix

## Issues Fixed

### 1. PORT Environment Variable Error
**Problem**: `Error: '$PORT' is not a valid port number`
**Root Cause**: Dockerfile was using array syntax `CMD ["gunicorn", ...]` which doesn't allow shell variable expansion
**Solution**: Changed to shell form `CMD gunicorn --bind 0.0.0.0:${PORT:-8080} ...` with fallback to 8080

### 2. Health Check Failures
**Problem**: `Readiness probe failed: dial tcp connection refused`
**Root Cause**: Missing run_command in app spec, causing container to not bind to correct port
**Solution**: Added explicit `run_command` in `.do/app.yaml`

## Final Deployment Steps

### Option 1: Using App Spec (Recommended)
1. Go to Digital Ocean App Platform
2. Create new app from GitHub
3. Import app spec from `.do/app.yaml`
4. Deploy

### Option 2: Manual Configuration
1. Create new app from GitHub: `astrobsm/mdcanreg_cert`
2. Let Digital Ocean detect Dockerfile
3. **IMPORTANT**: Add this as custom run command:
   ```
   gunicorn --bind 0.0.0.0:${PORT:-8080} digital_ocean_app:app
   ```
4. Deploy

## Environment Variables
These are already configured in your app spec:
- `DATABASE_URL`: Auto-generated from your PostgreSQL database
- `EMAIL_HOST`: smtp.gmail.com
- `EMAIL_PORT`: 587
- `EMAIL_USER`: mdcanenugu@gmail.com
- `EMAIL_PASSWORD`: [encrypted]
- `EMAIL_FROM`: [encrypted]

## Key Changes Made

1. **Dockerfile**: Changed CMD to shell form for proper PORT variable handling
2. **app.yaml**: Added explicit run_command with PORT fallback
3. **Entry Point**: Using `digital_ocean_app:app` as the application entry point

## Expected Results

After deployment:
- ✅ No more "$PORT is not a valid port number" errors
- ✅ Health checks should pass
- ✅ App should be accessible on the provided Digital Ocean URL
- ✅ Database connection should work automatically
- ✅ Email functionality should work with your Gmail SMTP settings

## Verification Steps

1. Check deployment logs for successful startup
2. Visit the app URL to verify it loads
3. Test the `/health` endpoint
4. Verify certificate generation functionality

The app should now deploy successfully without the PORT and health check issues.
