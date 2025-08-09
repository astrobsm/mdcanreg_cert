@echo off
echo Starting MDCAN BDM 2025 Development Environment...

echo.
echo [1/3] Starting Backend Server...
start "Backend" cmd /c "cd backend && python app.py"

echo [2/3] Starting Frontend Server...
start "Frontend" cmd /c "cd frontend && npm start"

echo [3/3] Servers starting...
echo.
echo ✅ Development environment started!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:5000
echo 💚 Health:   http://localhost:5000/api/health
echo.
echo Press any key to close this window...
pause >nul
