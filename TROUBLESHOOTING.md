# MDCAN BDM 2025 Certificate Platform - Troubleshooting Guide

## Minification Issues in Production Builds

If you encounter errors like `Cannot access 'z' before initialization` or `Cannot access 'loadParticipants' before initialization` in the production build, this is likely due to variable hoisting issues that occur during minification.

### Quick Fix: Use Development Mode Build

The quickest solution is to use a development build which doesn't minify the code. We've updated the `start-optimized-platform.bat` script to do this automatically.

To start the platform in development mode (with optimized backend):

```
start-optimized-platform.bat
```

### Understanding the Issue

The problem occurs because:

1. JavaScript's minification process rearranges variable declarations
2. React hooks and function declarations need to be in a specific order
3. When minified, these declarations get reordered, causing reference errors

### Permanent Solutions

For a more permanent solution, you can try any of these approaches:

1. **Initialize variables early**:
   - We've created a `setupProduction.js` file that gets imported first in `index.js`
   - This ensures all important variables are initialized before any component code runs

2. **Disable minification for production**:
   - Set `GENERATE_SOURCEMAP=true` and `REACT_APP_DISABLE_MINIFICATION=true` in your `.env.production` file
   - Use `build-safe.bat` which sets these environment variables before building

3. **Restructure your code**:
   - Make sure all function declarations happen before they're used in hooks
   - Use the React pattern where hooks are at the top of components
   - Avoid referencing variables before they're defined

## Flask Compatibility Issues

If you encounter `AttributeError: 'Flask' object has no attribute 'before_first_request'` error:

- This happens because Flask 2.x removed the `before_first_request` decorator
- Our `optimized_app.py` fixes this by using the app context approach instead:

```python
# Create the database tables - using Flask 2.x+ compatible approach
with app.app_context():
    db.create_all()
```

## Health Endpoint Issues

If the `/health` endpoint shows a different project:

1. Make sure you're running `optimized_app.py` and not another Flask application
2. Check if you have multiple Python processes running (use Task Manager)
3. Kill any existing Python processes before starting the platform:
   ```
   taskkill /F /IM python.exe
   ```
4. Verify the correct server is running by checking the health endpoint:
   ```
   http://localhost:5000/health
   ```
   It should show "project": "MDCAN BDM 2025 Certificate Platform"

## Need More Help?

If you continue to experience issues:

1. Check the browser console for specific error messages
2. Look at the terminal output from both frontend and backend servers
3. Try a clean rebuild by running:
   ```
   rebuild.bat
   ```
4. If all else fails, start from a clean development environment:
   ```
   reset-environment.bat
   start-development.bat
   ```
