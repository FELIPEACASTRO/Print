@echo off
chcp 65001 >nul
cls
echo ==========================================
echo   POKER VISION - GERENCIADOR DE SOLUCAO
echo ==========================================
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale o Python 3.8+ e adicione ao PATH.
    pause
    exit /b 1
)

:: Parar processos existentes
echo [1/4] Parando instancias anteriores...
taskkill /F /FI "WINDOWTITLE eq Poker Vision*" >nul 2>&1
timeout /t 2 /nobreak >nul

:: Iniciar API Externa
echo [2/4] Iniciando API Externa (Porta 8001)...
start "Poker Vision - API Externa" cmd /k "python external_api.py"

:: Aguardar inicialização
timeout /t 3 /nobreak >nul

:: Iniciar API Principal
echo [3/4] Iniciando API Principal (Porta 8000)...
start "Poker Vision - API Principal" cmd /k "python main.py"

echo.
echo [4/4] Sistemas iniciados!
echo.
echo ==========================================
echo   ACESSO: http://localhost:8000
echo   API EXT: http://localhost:8001
echo   LOGS: Verifique as janelas do terminal abertas
echo ==========================================
echo.
echo Para parar, execute: stop_solution.bat
echo.
pause