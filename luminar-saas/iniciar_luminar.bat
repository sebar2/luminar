@echo off
chcp 65001 >nul
title Luminar B2B Operations - Launcher
echo ============================================================
echo   Luminar Uruguay - Intelligence & Operations SaaS
echo   Iniciando Backend FastAPI y Frontend Web
echo ============================================================
echo.

set BASE_DIR=%~dp0
cd /d "%BASE_DIR%backend"

echo [1/2] Levantando Backend FastAPI en http://localhost:8000 ...
start "Luminar Backend FastAPI" cmd /k "chcp 65001 >nul && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

cd /d "%BASE_DIR%frontend"
start "Luminar Frontend Streamlit" cmd /k "chcp 65001 >nul && python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --browser.gatherUsageStats false"

timeout /t 3 >nul

echo.
echo ============================================================
echo   Plataforma iniciada con éxito!
echo   - Local (PC actual):  http://localhost:8501
echo   - Backend FastAPI:    http://localhost:8000 (Docs: /docs)
echo.
echo   - Acceso Remoto / Tailscale VPN (Notebook y Celular APK):
echo     http://[TU-IP-TAILSCALE]:8501
echo     (Para ver tu IP de Tailscale, abre la app de Tailscale en tu PC)
echo ============================================================
echo.
echo Abriendo la aplicación en tu navegador...
start http://localhost:8501

pause
