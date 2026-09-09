@echo off
title ERP System - Setup & Run
color 0A

echo ============================================
echo   ERP System - Professional Services
echo   Complete Setup & Run Script
echo ============================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running as Administrator
) else (
    echo [WARN] Not running as Administrator
    echo        Some operations may fail.
    echo        Right-click and "Run as Administrator" for best results.
    echo.
)

REM Check prerequisites
echo Checking prerequisites...

where docker >nul 2>&1 && set HAS_DOCKER=1
where docker-compose >nul 2>&1 && set HAS_COMPOSE=1
where php >nul 2>&1 && set HAS_PHP=1
where composer >nul 2>&1 && set HAS_COMPOSER=1
where node >nul 2>&1 && set HAS_NODE=1
where npm >nul 2>&1 && set HAS_NPM=1

if defined HAS_DOCKER if defined HAS_COMPOSE (
    echo [OK] Docker & Docker Compose found
    set USE_DOCKER=1
) else if defined HAS_PHP if defined HAS_COMPOSER if defined HAS_NODE if defined HAS_NPM (
    echo [OK] PHP, Composer, Node.js, npm found
    set USE_DOCKER=0
) else (
    echo [ERROR] Missing prerequisites!
    echo.
    echo Required (choose one):
    echo   Option 1: Docker Desktop + Docker Compose
    echo   Option 2: PHP 8.2+, Composer, Node.js 18+, npm
    echo.
    pause
    exit /b 1
)

echo.
echo Project root: %CD%
echo.

if "%USE_DOCKER%"=="1" (
    echo ============================================
    echo   STARTING WITH DOCKER
    echo ============================================
    echo.
    
    echo Starting containers...
    docker-compose up -d
    
    echo Waiting for MySQL to be ready...
    set WAITED=0
    :WAIT_MYSQL
    docker inspect --format="{{.State.Health.Status}}" erp-mysql 2>nul | find "healthy" >nul
    if %errorLevel%==0 (
        echo MySQL is healthy!
    ) else (
        if %WAITED% GEQ 120 (
            echo MySQL failed to become healthy in time
            pause
            exit /b 1
        )
        timeout /t 5 /nobreak >nul
        set /a WAITED+=5
        echo Waiting... (%WAITED%/120 sec)
        goto WAIT_MYSQL
    )
    
    echo Running migrations & seeders...
    docker-compose exec -T backend php artisan migrate --seed --force
    
    echo Creating storage link...
    docker-compose exec -T backend php artisan storage:link
    
    echo Clearing caches...
    docker-compose exec -T backend php artisan config:clear
    docker-compose exec -T backend php artisan route:clear
    docker-compose exec -T backend php artisan view:clear
    
    goto SHOW_SUCCESS
)

echo ============================================
echo   MANUAL SETUP
echo ============================================
echo.

cd backend
echo Installing PHP dependencies...
composer install --no-interaction

if not exist .env (
    copy .env.example .env
)

echo Generating application key...
php artisan key:generate --force

echo Configuring database...
REM Update .env with PowerShell for better string handling
powershell -Command "
    $envContent = Get-Content .env -Raw
    $envContent = $envContent -replace 'DB_CONNECTION=.*', 'DB_CONNECTION=mysql'
    $envContent = $envContent -replace 'DB_HOST=.*', 'DB_HOST=127.0.0.1'
    $envContent = $envContent -replace 'DB_PORT=.*', 'DB_PORT=3306'
    $envContent = $envContent -replace 'DB_DATABASE=.*', 'DB_DATABASE=erp_system'
    $envContent = $envContent -replace 'DB_USERNAME=.*', 'DB_USERNAME=root'
    $envContent = $envContent -replace 'DB_PASSWORD=.*', 'DB_PASSWORD=secret'
    $envContent | Set-Content .env -Encoding UTF8
"

echo Creating database...
mysql -u root -psecret -e "CREATE DATABASE IF NOT EXISTS erp_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo Running migrations & seeders...
php artisan migrate --seed --force

echo Creating storage link...
php artisan storage:link

echo Clearing caches...
php artisan config:clear
php artisan route:clear
php artisan view:clear

cd ..\frontend
echo Installing Node dependencies...
npm install

if not exist .env (
    copy .env.example .env
)

cd ..

:SHOW_SUCCESS
echo.
echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo API:       http://localhost:8000/api
echo.
echo Login Credentials:
echo   Admin:     admin@erp.local / password123
echo   Manager:   pm1@erp.local  / password123
echo   Developer: dev1@erp.local / password123
echo.
echo To start servers manually:
echo   Backend:  cd backend && php artisan serve
echo   Frontend: cd frontend && npm run dev
echo.
pause