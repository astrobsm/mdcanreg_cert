# MDCAN BDM 2025 Certificate Platform - Automation Scripts

This directory contains automated scripts to streamline the development process.

## Available Scripts

### 🚀 `start-development.bat` - **RECOMMENDED FOR FIRST TIME**
**Complete setup and startup script for first-time users**

- Automatically detects if this is the first run
- Installs all frontend dependencies (`npm install`)
- Builds the React application (`npm run build`)
- Installs all backend dependencies (`pip install -r requirements.txt`)
- Sets up the database and creates `.env` file
- Starts the Flask backend server
- Opens the application at `http://localhost:5000`

**Usage:** Double-click or run from command prompt
```cmd
start-development.bat
```

### ⚡ `start-quick.bat` - **DAILY USE**
**Quick startup for production mode (after initial setup)**

- Checks if build exists, rebuilds if necessary
- Verifies `.env` configuration exists
- Starts Flask backend server only
- Application runs at `http://localhost:5000`

**Usage:** Double-click or run from command prompt
```cmd
start-quick.bat
```

### 🔧 `start-dev-mode.bat` - **DEVELOPMENT MODE**
**Development mode with hot reload for both frontend and backend**

- Starts Flask backend server (`http://localhost:5000`)
- Starts React development server (`http://localhost:3000`)
- Both servers run in separate windows
- Frontend has hot reload for development

**Usage:** Double-click or run from command prompt
```cmd
start-dev-mode.bat
```

### 🧹 `reset-environment.bat` - **TROUBLESHOOTING**
**Clean up and reset the development environment**

- Removes `node_modules` directory
- Removes `build` directory
- Removes Python cache files
- Removes `.env` file
- Useful for troubleshooting or starting fresh

**Usage:** Double-click or run from command prompt
```cmd
reset-environment.bat
```

## Quick Start Guide

### For First Time Setup:
1. Double-click `start-development.bat`
2. Wait for setup to complete
3. Edit `backend\.env` with your Gmail app password
4. Visit `http://localhost:5000`

### For Daily Development:
1. Double-click `start-quick.bat`
2. Visit `http://localhost:5000`

### For Active Development (with hot reload):
1. Double-click `start-dev-mode.bat`
2. Use `http://localhost:3000` for frontend development
3. API calls will proxy to `http://localhost:5000`

## Manual Commands (Alternative)

If you prefer manual control:

### Backend Only:
```cmd
cd backend
python app.py
```

### Frontend Development:
```cmd
cd frontend
npm start
```

### Build Frontend:
```cmd
cd frontend
npm run build
```

## Troubleshooting

### If something goes wrong:
1. Run `reset-environment.bat`
2. Run `start-development.bat` again

### Common Issues:
- **Port 5000 in use**: Close other Flask applications or change port in `backend/app.py`
- **Database connection errors**: Check PostgreSQL is running and credentials in `.env`
- **Missing dependencies**: Run `reset-environment.bat` then `start-development.bat`

## Environment Files

After running `start-development.bat`, you'll need to configure:

- `backend\.env` - Update with your actual Gmail app password and database credentials
- Replace placeholder images in `frontend/public/` and `public/` directories with actual logos and signatures

## Notes

- The automated scripts handle both first-time setup and daily usage
- All scripts include error checking and user-friendly messages
- Scripts automatically detect the current state and adapt accordingly
- Backend serves the built React app in production mode
- Development mode runs both servers separately for hot reload
