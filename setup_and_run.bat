@echo off
set CREATE_ADMIN=true
set ADMIN_USER=admin
set ADMIN_EMAIL=admin@admin.com
set ADMIN_PASS=admin

setlocal enabledelayedexpansion

set SEED=true

set HOST=%1
if "!HOST!"=="" set HOST=127.0.0.1

set PORT=%2
if "!PORT!"=="" set PORT=8000

echo [setup] project dir: %CD%

py --version >nul 2>&1
if errorlevel 1 (
  python --version >nul 2>&1
  if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
      echo Error: Python not found on PATH
      exit /b 1
    )
    set PYTHON=python3
  ) else (
    set PYTHON=python
  )
) else (
  set PYTHON=py
)

echo [setup] using Python: !PYTHON!

set VENV_DIR=.venv

if not exist "!VENV_DIR!" (
  echo [setup] creating virtualenv in !VENV_DIR!...
  !PYTHON! -m venv !VENV_DIR!
)

echo [setup] upgrading pip...
!VENV_DIR!\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

if exist requirements.txt (
  echo [setup] installing requirements.txt...
  !VENV_DIR!\Scripts\python.exe -m pip install -r requirements.txt
) else (
  echo [setup] no requirements.txt found, skipping install
)

echo [setup] applying migrations...
!VENV_DIR!\Scripts\python.exe manage.py migrate --noinput

REM Create superuser if CREATE_ADMIN is true
if "!CREATE_ADMIN!"=="true" (
  if "!ADMIN_USER!"=="" set ADMIN_USER=admin
  if "!ADMIN_EMAIL!"=="" set ADMIN_EMAIL=admin@example.com
  if "!ADMIN_PASS!"=="" set ADMIN_PASS=admin
  
  echo [setup] creating superuser '!ADMIN_USER!' (if not exists)...
  !VENV_DIR!\Scripts\python.exe manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); u='!ADMIN_USER!'; e='!ADMIN_EMAIL!'; p='!ADMIN_PASS!'; User.objects.filter(username=u).exists() or User.objects.create_superuser(u,e,p)"
)

REM Run seed script if SEED is true
if "!SEED!"=="true" (
  if exist seed_data.py (
    echo [setup] running seed_data.py...
    !VENV_DIR!\Scripts\python.exe seed_data.py
  )
)

echo [run] starting Django dev server on !HOST!:!PORT!
!VENV_DIR!\Scripts\python.exe manage.py runserver !HOST!:!PORT!
