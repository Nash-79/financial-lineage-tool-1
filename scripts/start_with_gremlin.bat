@echo off
echo ================================================================
echo   Starting Financial Lineage Tool with Gremlin Server
echo ================================================================
echo.

echo [1/5] Checking Docker Desktop...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Desktop is not running!
    echo Please start Docker Desktop and wait until it's fully initialized.
    echo Then run this script again.
    pause
    exit /b 1
)
echo [OK] Docker is running

echo.
echo [2/5] Starting Docker services (Gremlin, Qdrant, Redis)...
docker compose -f docker-compose.local.yml up -d gremlin-server qdrant redis
if errorlevel 1 (
    echo ERROR: Failed to start Docker services
    pause
    exit /b 1
)

echo.
echo [3/5] Waiting 15 seconds for Gremlin Server to initialize...
timeout /t 15 /nobreak >nul

echo.
echo [4/5] Verifying Gremlin Server is ready...
docker logs gremlin-server --tail 5

echo.
echo [5/5] Starting API with Gremlin integration...
echo.
echo ================================================================
echo   API will start now. Watch for:
echo   [+] Gremlin client connected successfully
echo   [+] Connected to Gremlin Server
echo ================================================================
echo.

python src\api\main_local.py
