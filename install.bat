@echo off
echo 📦 Setting up Railway Booking System...

REM Step 1: Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Step 2: Install dependencies
pip install -r requirements.txt

REM Step 3: Copy .env template
copy .env.example .env
echo ✅ .env file created. Please edit it with your MySQL credentials.
pause

REM Step 4: Read .env values using PowerShell
for /f "delims=" %%i in ('powershell -Command "(Get-Content .env) -match '^MYSQL_USER=' | foreach { ($_ -split '=')[1] }"') do set MYSQL_USER=%%i
for /f "delims=" %%i in ('powershell -Command "(Get-Content .env) -match '^MYSQL_PASSWORD=' | foreach { ($_ -split '=')[1] }"') do set MYSQL_PASSWORD=%%i
for /f "delims=" %%i in ('powershell -Command "(Get-Content .env) -match '^MYSQL_HOST=' | foreach { ($_ -split '=')[1] }"') do set MYSQL_HOST=%%i

REM Step 5: Run schema.sql
echo 🛠️  Creating tables using MySQL CLI...
mysql -h %MYSQL_HOST% -u %MYSQL_USER% -p%MYSQL_PASSWORD% < schema.sql
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to execute schema.sql. Please check credentials and MySQL status.
    exit /b 1
)

REM Step 6: Start the app
echo ✅ Database and tables created.
python run.py
