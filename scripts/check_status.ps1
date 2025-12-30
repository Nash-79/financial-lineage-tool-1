# Status Check Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Financial Lineage Tool - Status Check" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Ollama
Write-Host "1. Ollama Status:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "   [OK] Ollama is running" -ForegroundColor Green
    Write-Host "   Models available:"
    foreach ($model in $response.models) {
        Write-Host "   - $($model.name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   [X] Ollama not running" -ForegroundColor Red
    Write-Host "   Start it from Windows Start Menu or run: ollama serve"
}

Write-Host ""

# Check Docker
Write-Host "2. Docker Status:" -ForegroundColor Yellow
$dockerRunning = $false
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Docker is running" -ForegroundColor Green
        $dockerRunning = $true
    } else {
        Write-Host "   [X] Docker not running" -ForegroundColor Red
    }
} catch {
    Write-Host "   [X] Docker not installed or not running" -ForegroundColor Red
}

Write-Host ""

# Check Qdrant
Write-Host "3. Qdrant (Vector DB) Status:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:6333/health" -TimeoutSec 5
    Write-Host "   [OK] Qdrant is running on port 6333" -ForegroundColor Green
} catch {
    Write-Host "   [X] Qdrant not running" -ForegroundColor Red
    if ($dockerRunning) {
        Write-Host "   To start: docker run -d -p 6333:6333 qdrant/qdrant" -ForegroundColor Gray
    }
}

Write-Host ""

# Check Gremlin
Write-Host "4. Gremlin Server (Graph DB) Status:" -ForegroundColor Yellow
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 8182)
    $tcpClient.Close()
    Write-Host "   [OK] Gremlin Server is running on port 8182" -ForegroundColor Green
} catch {
    Write-Host "   [X] Gremlin Server not running" -ForegroundColor Red
    if ($dockerRunning) {
        Write-Host "   To start: docker run -d -p 8182:8182 tinkerpop/gremlin-server" -ForegroundColor Gray
    }
}

Write-Host ""

# Check Python venv
Write-Host "5. Python Environment:" -ForegroundColor Yellow
$venvPython = ".\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "   [OK] Virtual environment exists" -ForegroundColor Green
    $version = & $venvPython --version 2>&1
    Write-Host "   $version" -ForegroundColor Gray
} else {
    Write-Host "   [X] Virtual environment not found" -ForegroundColor Red
    Write-Host "   Run: python -m venv venv" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To start the API:" -ForegroundColor White
Write-Host "  .\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "  pip install -r requirements-local.txt" -ForegroundColor Gray
Write-Host "  python -m uvicorn src.api.main_local:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "  Then open: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
