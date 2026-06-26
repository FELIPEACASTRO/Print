@echo off
echo ==========================================
echo   POKER VISION - PARANDO SERVICOS
echo ==========================================
echo.

echo [1/2] Parando API Principal...
taskkill /F /FI "WINDOWTITLE eq Poker Vision - API Principal*" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] API Principal nao estava em execucao.
) else (
    echo [OK] API Principal parada.
)

echo [2/2] Parando API Externa...
taskkill /F /FI "WINDOWTITLE eq Poker Vision - API Externa*" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] API Externa nao estava em execucao.
) else (
    echo [OK] API Externa parada.
)

echo.
echo ==========================================
echo   Todos os servicos foram parados.
echo ==========================================
echo.
pause