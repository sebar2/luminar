@echo off
chcp 65001 >nul
title Luminar B2B Operations - Desktop WebApp Launcher

set CONFIG_FILE=%~dp0tailscale_ip.txt

if exist "%CONFIG_FILE%" (
    set /p SERVER_IP=<"%CONFIG_FILE%"
)

if "%SERVER_IP%"=="" (
    echo ============================================================
    echo   Luminar B2B Operations - Configuración de Acceso Remoto
    echo ============================================================
    echo.
    echo Ingrese la IP de Tailscale de la PC servidora (ejemplo: pon tu ip aqui o 100.x.y.z)
    echo O presione ENTER para usar localhost (si corre en esta misma PC):
    set /p INPUT_IP="> "
    if "%INPUT_IP%"=="" (
        set SERVER_IP=localhost
    ) else (
        set SERVER_IP=%INPUT_IP%
    )
    echo %SERVER_IP%> "%CONFIG_FILE%"
)

set TARGET_URL=http://%SERVER_IP%:8501

echo Iniciando Luminar WebApp en: %TARGET_URL%

:: Detectar navegador disponible para lanzar en modo standalone app (sin barras ni pestañas)
set BROWSER_EXE=

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_EXE=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_EXE=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
)

if not "%BROWSER_EXE%"=="" (
    start "" "%BROWSER_EXE%" --app=%TARGET_URL% --window-size=1280,800
) else (
    start %TARGET_URL%
)

exit
