<# 
ERP System - Complete Setup & Run Script for Windows
Run this script as Administrator in PowerShell
#>

param(
    [switch]$UseDocker,
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [string]$MySqlPassword = "secret",
    [string]$DbName = "erp_system"
)

$ErrorActionPreference = "Stop"
$projectRoot = "C:\Users\MANAS GAIKWAD\Documents\Default Project\erp-system"

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "  ERP System - Professional Services" -ForegroundColor Cyan
Write-Host "  Complete Setup & Run Script" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Not running as Administrator. Some operations may fail."
    Write-Host "Re-run PowerShell as Administrator for best results." -ForegroundColor Yellow
    Write-Host ""
}

# Function to check if command exists
function Check-Command($cmd, $name) {
    try {
        $result = Get-Command $cmd -ErrorAction Stop
        Write-Host "✓ $name found: $($result.Source)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ $name NOT found" -ForegroundColor Red
        return $false
    }
}

# Function to run command with output
function Run-Command($cmd, $description, $workingDir = $null) {
    Write-Host "`n▶ $description..." -ForegroundColor Yellow
    try {
        if ($workingDir) {
            Push-Location $workingDir
        }
        $result = Invoke-Expression $cmd
        if ($workingDir) {
            Pop-Location
        }
        Write-Host "✓ Completed" -ForegroundColor Green
        return $true
    } catch {
        if ($workingDir) { Pop-Location }
        Write-Host "✗ FAILED: $_" -ForegroundColor Red
        return $false
    }
}

# ============================================
# PREREQUISITE CHECKS
# ============================================
Write-Host "`n=== CHECKING PREREQUISITES ===" -ForegroundColor Cyan

$hasDocker = Check-Command "docker" "Docker"
$hasDockerCompose = Check-Command "docker-compose" "Docker Compose"
$hasPhp = Check-Command "php" "PHP"
$hasComposer = Check-Command "composer" "Composer"
$hasNode = Check-Command "node" "Node.js"
$hasNpm = Check-Command "npm" "npm"
$hasMysql = Check-Command "mysql" "MySQL Client"

if ($UseDocker -and ($hasDocker -and $hasDockerCompose)) {
    Write-Host "`nUsing Docker mode..." -ForegroundColor Cyan
    $dockerMode = $true
} else {
    Write-Host "`nUsing Manual mode..." -ForegroundColor Cyan
    $dockerMode = $false
    
    if (-not $hasPhp) {
        Write-Error "PHP 8.2+ is required. Download from https://windows.php.net/download/"
        exit 1
    }
    if (-not $hasComposer) {
        Write-Error "Composer is required. Download from https://getcomposer.org/download/"
        exit 1
    }
    if (-not $hasNode) {
        Write-Error "Node.js 18+ is required. Download from https://nodejs.org/"
        exit 1
    }
}

# ============================================
# DOCKER MODE
# ============================================
if ($dockerMode) {
    Write-Host "`n=== DOCKER SETUP ===" -ForegroundColor Cyan
    
    Push-Location $projectRoot
    
    # Start services
    Run-Command "docker-compose up -d" "Starting Docker containers"
    
    # Wait for MySQL to be healthy
    Write-Host "`n⏳ Waiting for MySQL to be ready..." -ForegroundColor Yellow
    $maxWait = 120
    $waited = 0
    while ($waited -lt $maxWait) {
        $health = docker inspect --format='{{.State.Health.Status}}' erp-mysql 2>$null
        if ($health -eq "healthy") {
            Write-Host "✓ MySQL is healthy" -ForegroundColor Green
            break
        }
        Start-Sleep 5
        $waited += 5
        Write-Host "  Waiting... ($waited/$maxWait sec)"
    }
    
    if ($waited -ge $maxWait) {
        Write-Error "MySQL failed to become healthy in time"
        exit 1
    }
    
    # Run migrations
    Run-Command "docker-compose exec -T backend php artisan migrate --seed --force" "Running migrations & seeders"
    
    # Storage link
    Run-Command "docker-compose exec -T backend php artisan storage:link" "Creating storage link"
    
    # Clear caches
    Run-Command "docker-compose exec -T backend php artisan config:clear" "Clearing config cache"
    Run-Command "docker-compose exec -T backend php artisan route:clear" "Clearing route cache"
    Run-Command "docker-compose exec -T backend php artisan view:clear" "Clearing view cache"
    
    Pop-Location
    
    Write-Host "`n===========================================" -ForegroundColor Cyan
    Write-Host "  DOCKER SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host "Frontend:  http://localhost:5173" -ForegroundColor Cyan
    Write-Host "Backend:   http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API:       http://localhost:8000/api" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Login Credentials:" -ForegroundColor Yellow
    Write-Host "  Admin:     admin@erp.local / password123"
    Write-Host "  Manager:   pm1@erp.local  / password123"
    Write-Host "  Developer: dev1@erp.local / password123"
    Write-Host ""
    Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Gray
    Write-Host "To stop:      docker-compose down" -ForegroundColor Gray
    exit 0
}

# ============================================
# MANUAL MODE
# ============================================
Write-Host "`n=== MANUAL SETUP ===" -ForegroundColor Cyan

# --- BACKEND SETUP ---
if (-not $SkipBackend) {
    Write-Host "`n=== BACKEND SETUP ===" -ForegroundColor Cyan
    $backendDir = Join-Path $projectRoot "backend"
    
    if (-not (Test-Path $backendDir)) {
        Write-Error "Backend directory not found: $backendDir"
        exit 1
    }
    
    Push-Location $backendDir
    
    # Install dependencies
    Run-Command "composer install --no-interaction" "Installing PHP dependencies"
    
    # Setup .env
    if (-not (Test-Path ".env")) {
        Run-Command "Copy-Item .env.example .env" "Creating .env file"
    }
    
    # Generate key
    Run-Command "php artisan key:generate --force" "Generating application key"
    
    # Update .env with database config
    Write-Host "`n📝 Configuring database..." -ForegroundColor Yellow
    $envContent = Get-Content .env -Raw
    
    $envContent = $envContent -replace 'DB_CONNECTION=.*', "DB_CONNECTION=mysql"
    $envContent = $envContent -replace 'DB_HOST=.*', "DB_HOST=127.0.0.1"
    $envContent = $envContent -replace 'DB_PORT=.*', "DB_PORT=3306"
    $envContent = $envContent -replace 'DB_DATABASE=.*', "DB_DATABASE=$DbName"
    $envContent = $envContent -replace 'DB_USERNAME=.*', "DB_USERNAME=root"
    $envContent = $envContent -replace 'DB_PASSWORD=.*', "DB_PASSWORD=$MySqlPassword"
    
    # Use file cache/queue if Redis not available
    if (-not (Get-Command "redis-cli" -ErrorAction SilentlyContinue)) {
        $envContent = $envContent -replace 'CACHE_DRIVER=.*', "CACHE_DRIVER=file"
        $envContent = $envContent -replace 'QUEUE_CONNECTION=.*', "QUEUE_CONNECTION=sync"
        $envContent = $envContent -replace 'SESSION_DRIVER=.*', "SESSION_DRIVER=file"
        Write-Host "  Using file-based cache/queue (Redis not found)" -ForegroundColor Yellow
    }
    
    $envContent | Set-Content .env -Encoding UTF8
    Write-Host "✓ .env configured" -ForegroundColor Green
    
    # Create database
    Write-Host "`n🗄️ Creating database..." -ForegroundColor Yellow
    try {
        $mysqlCmd = "mysql -u root -p$MySqlPassword -e `"CREATE DATABASE IF NOT EXISTS $DbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`""
        Invoke-Expression $mysqlCmd
        Write-Host "✓ Database created/verified" -ForegroundColor Green
    } catch {
        Write-Warning "Could not create database automatically. Please create manually:"
        Write-Host "  CREATE DATABASE $DbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    }
    
    # Run migrations
    Run-Command "php artisan migrate --seed --force" "Running migrations & seeders"
    
    # Storage link
    Run-Command "php artisan storage:link" "Creating storage link"
    
    # Clear caches
    Run-Command "php artisan config:clear" "Clearing config cache"
    Run-Command "php artisan route:clear" "Clearing route cache"
    Run-Command "php artisan view:clear" "Clearing view cache"
    
    Pop-Location
    Write-Host "`n✓ BACKEND SETUP COMPLETE" -ForegroundColor Green
}

# --- FRONTEND SETUP ---
if (-not $SkipFrontend) {
    Write-Host "`n=== FRONTEND SETUP ===" -ForegroundColor Cyan
    $frontendDir = Join-Path $projectRoot "frontend"
    
    if (-not (Test-Path $frontendDir)) {
        Write-Error "Frontend directory not found: $frontendDir"
        exit 1
    }
    
    Push-Location $frontendDir
    
    # Install dependencies
    Run-Command "npm install" "Installing Node dependencies"
    
    # Setup .env
    if (-not (Test-Path ".env")) {
        Run-Command "Copy-Item .env.example .env" "Creating frontend .env"
    }
    
    # Build for production (optional)
    # Run-Command "npm run build" "Building for production"
    
    Pop-Location
    Write-Host "`n✓ FRONTEND SETUP COMPLETE" -ForegroundColor Green
}

# ============================================
# START SERVERS
# ============================================
Write-Host "`n=== STARTING SERVERS ===" -ForegroundColor Cyan

$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

# Start Backend in background
if (-not $SkipBackend) {
    Write-Host "`n🚀 Starting Laravel backend on http://localhost:8000..." -ForegroundColor Cyan
    $backendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        php artisan serve --host=0.0.0.0 --port=8000
    } -ArgumentList $backendDir
    
    # Wait a moment for server to start
    Start-Sleep 3
    
    # Test backend
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"admin@erp.local","password":"password123"}' -TimeoutSec 10
        Write-Host "✓ Backend is running and responding" -ForegroundColor Green
    } catch {
        Write-Warning "Backend may still be starting. Check manually at http://localhost:8000"
    }
}

# Start Frontend in background
if (-not $SkipFrontend) {
    Write-Host "`n🚀 Starting Vite frontend on http://localhost:5173..." -ForegroundColor Cyan
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        npm run dev -- --host 0.0.0.0 --port 5173
    } -ArgumentList $frontendDir
    
    Start-Sleep 3
    Write-Host "✓ Frontend started" -ForegroundColor Green
}

# ============================================
# SUMMARY
# ============================================
Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host "  ERP SYSTEM IS RUNNING!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   API:       http://localhost:8000/api" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Demo Login Credentials:" -ForegroundColor Yellow
Write-Host "   Super Admin:  admin@erp.local    / password123" -ForegroundColor White
Write-Host "   Admin:        admin2@erp.local   / password123" -ForegroundColor White
Write-Host "   Project Mgr:  pm1@erp.local      / password123" -ForegroundColor White
Write-Host "   Team Lead:    tl1@erp.local      / password123" -ForegroundColor White
Write-Host "   Sr Consultant: sc1@erp.local     / password123" -ForegroundColor White
Write-Host "   Consultant:   dev1@erp.local     / password123" -ForegroundColor White
Write-Host ""
Write-Host "📋 Running Jobs:" -ForegroundColor Gray
if ($backendJob) { Write-Host "   Backend Job ID: $($backendJob.Id)" -ForegroundColor Gray }
if ($frontendJob) { Write-Host "   Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Gray }
Write-Host ""
Write-Host "To stop servers: Press Ctrl+C or run:" -ForegroundColor Gray
Write-Host "   Stop-Job -Id $($backendJob.Id), $($frontendJob.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers..." -ForegroundColor Gray

# Keep script running
try {
    while ($true) { Start-Sleep 10 }
} finally {
    if ($backendJob) { Stop-Job $backendJob }
    if ($frontendJob) { Stop-Job $frontendJob }
    Write-Host "`n👋 Servers stopped. Goodbye!" -ForegroundColor Cyan
}