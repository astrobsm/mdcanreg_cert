@echo off
echo Setting up MDCAN BDM 2025 Certificate Platform Backend...

cd backend

echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo To run the backend server:
echo 1. Navigate to backend directory: cd backend
echo 2. Activate virtual environment: venv\Scripts\activate
echo 3. Copy .env.example to .env and configure your settings
echo 4. Install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html
echo 5. Run the server: python app.py
echo.
pause
