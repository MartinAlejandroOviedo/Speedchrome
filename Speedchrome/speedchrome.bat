@echo off

rem Verificar si el sistema es x64
if not "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    echo Este script solo es compatible con procesadores x64.
    exit /b
)

rem Solicitar confirmación antes de continuar
echo Este script realizará los siguientes cambios en los navegadores compatibles:
echo - Establecer el límite de memoria de Chromium a 4 GB
echo - Deshabilitar la precarga de páginas
echo - Deshabilitar la aceleración de hardware
echo.
set /p "respuesta=¿Desea continuar? (S/N): "

if /i "%respuesta%"=="N" (
    echo Cancelando...
    exit /b
)

rem Lista de navegadores
set browsers=Microsoft\Edge Google\Chrome BraveSoftware\Brave Software\Opera

rem Aplicar configuraciones a cada navegador compatible
for %%b in (%browsers%) do (
    set "browser=%%b"
    call :ConfigureBrowser
)

goto :End

rem Función para aplicar configuraciones a un navegador basado en Chromium
:ConfigureBrowser
    echo Procesando configuraciones para el navegador: %browser%

    rem Verificar y deshabilitar la aceleración de hardware si ya no está deshabilitada
    set "reg_path=HKLM\SOFTWARE\%browser%\HardwareAcceleration"
    echo Ruta de registro: %reg_path%
    for /f "tokens=3" %%a in ('REG QUERY "%reg_path%" /v EnableHardwareAcceleration 2^>nul') do set "value=%%a"
    if defined value (
        if "%value%"=="0x0" (
            echo La aceleración de hardware ya está deshabilitada para %browser%.
        ) else (
            echo Deshabilitando la aceleración de hardware para %browser%...
            REG ADD "%reg_path%" /v EnableHardwareAcceleration /t REG_DWORD /d 0 /f
        )
    ) else (
        echo La clave de aceleración de hardware no existe, creando y deshabilitando para %browser%...
        REG ADD "%reg_path%" /v EnableHardwareAcceleration /t REG_DWORD /d 0 /f
    )

    rem Establecer el límite de memoria del proceso a 4 GB
    set "process_path=HKLM\SOFTWARE\%browser%\Process"
    echo Configurando límite de memoria en 4 GB para %browser% en %process_path%...
    REG ADD "%process_path%" /v MaxMemPerProcess /t REG_DWORD /d 4096 /f

    rem Deshabilitar la precarga de páginas
    set "prefetch_path=HKLM\SOFTWARE\%browser%\Prefetch"
    echo Deshabilitando la precarga de páginas para %browser% en %prefetch_path%...
    REG ADD "%prefetch_path%" /v EnablePrefetch /t REG_DWORD /d 0 /f

    goto :eof

:End
rem Mensaje final
echo.
echo Los cambios se han realizado correctamente en los navegadores detectados.
echo Por favor, reinicie los navegadores para que los cambios surtan efecto.
echo.
set /p "reiniciar=¿Desea reiniciar los navegadores ahora? (S/N): "

if /i "%reiniciar%"=="S" (
    for %%b in (msedge.exe chrome.exe brave.exe opera.exe) do (
        taskkill /F /IM %%b 2>nul
    )
    echo Los navegadores se están reiniciando...
) else (
    echo Por favor, reinicie los navegadores manualmente para aplicar los cambios.
)