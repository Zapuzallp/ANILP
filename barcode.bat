@echo off
REM Activate the virtual environment
call "C:\path\to\your\venv\Scripts\activate.bat"

REM Navigate to the project directory
cd /d "C:\path\to\your\django\project"

REM Run migrations
python manage.py migrate

REM Start the Django development server
python manage.py runserver 0.0.0.0:8000