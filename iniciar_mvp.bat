@echo off
title RacePulse AI - MVP Funcional (Hito 3) - Localhost
cd /d "%~dp0"
echo ======================================================================
echo    RACEPULSE AI - SISTEMA INTELIGENTE DE PREDICCION HIPICA
echo    Hito 3: Solucion Final, Evaluacion y MVP Funcional
echo    PTIA - Grupo 2 (Kevin Andrey Angel / Nicolas Santiago Sanchez)
echo ======================================================================
echo.
echo Iniciando servidor web en http://localhost:8000 ...
echo Abriendo aplicacion en el navegador...
echo.
echo Para detener el servidor, presiona Ctrl + C en esta ventana.
echo ======================================================================
echo.
python app.py
pause
