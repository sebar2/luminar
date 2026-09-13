@echo off
chcp 65001 >nul
title Compilador APK Luminar Android

echo ============================================================
echo   Compilando APK de Luminar B2B para Android...
echo ============================================================

set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
set PATH=%JAVA_HOME%\bin;%PATH%
set MOBILE_DIR=%~dp0luminar-mobile

cd /d "%MOBILE_DIR%"
call gradlew.bat assembleDebug

if exist "%MOBILE_DIR%\app\build\outputs\apk\debug\app-debug.apk" (
    copy /y "%MOBILE_DIR%\app\build\outputs\apk\debug\app-debug.apk" "%~dp0Luminar-v1.0.apk" >nul
    echo.
    echo ============================================================
    echo   [OK] APK compilado exitosamente!
    echo   Archivo generado: %~dp0Luminar-v1.0.apk
    echo ============================================================
) else (
    echo.
    echo [ERROR] No se pudo compilar el APK. Revisa los mensajes anteriores.
)

pause
