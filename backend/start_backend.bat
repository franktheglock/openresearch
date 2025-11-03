@echo off
REM start_backend.bat - Start the FastAPI backend (uvicorn) with optional venv activation
REM Usage: start_backend.bat [port] [--bg] [--reload]
REM Examples:
REM   start_backend.bat              -> starts on port 8000
REM   start_backend.bat 3000        -> starts on port 3000
REM   start_backend.bat 8000 --bg   -> starts in a new window (background)
REM   start_backend.bat 8000 --reload -> starts with reload enabled (dev only)

setlocal enabledelayedexpansion

:: Default values
set "PORT=8081"
set "BG_FLAG=0"
set "RELOAD_FLAG=0"

:: Parse args (allow any order)
for %%A in (%*) do (
    if "%%~A"=="--bg" set "BG_FLAG=1"
    if "%%~A"=="--reload" set "RELOAD_FLAG=1"
    if not "%%~A"=="--bg" if not "%%~A"=="--reload" (
        REM first non-flag arg is taken as port if numeric
        set "ARG=%%~A"
        for /f "delims=" %%N in ('echo %%ARG%%') do set "ARG=%%N"
        rem check if ARG is all digits
        set "ISNUM=1"
        for /f "delims=0123456789" %%I in ("%%ARG%%") do set "ISNUM=0"
        if "!ISNUM!"=="1" set "PORT=%%~A"
    )
)

:: Try to activate venv if exists at venv\Scripts\activate.bat or .venv\Scripts\activate.bat
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

:: Find an available port (try PORT up to PORT+100)
set "FOUND_PORT=0"
set /a END=%PORT%+100
for /l %%P in (%PORT%,1,%END%) do (
    rem check if port %%P is listening
    netstat -ano | findstr /r /c:":%%P " >nul
    if errorlevel 1 (
        rem port %%P seems free
        set "PORT=%%P"
        set "FOUND_PORT=1"
        goto :PORT_FOUND
    )
)
:PORT_FOUND
if "%FOUND_PORT%"=="0" (
    echo ERROR: Could not find a free port in the range %PORT%..%END%.
    endlocal
    goto :EOF
)

:: Build command after we have the chosen port
set "CMD=python -m uvicorn app.main:app --host 0.0.0.0 --port %PORT%"
if "%RELOAD_FLAG%"=="1" (
    set "CMD=%CMD% --reload"
)

:: If background requested, use start to open new window
if "%BG_FLAG%"=="1" (
    echo Starting backend in new window on port %PORT%...
    start "FastAPI Backend" cmd /c "%CMD%"
    endlocal
    goto :EOF
)

echo Starting backend on port %PORT%...
echo Command: %CMD%
:: Check if port is already in use (Windows)
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":%PORT% "') do (
    set "OCC_PID=%%p"
)
if defined OCC_PID (
    echo ERROR: Port %PORT% appears to be in use by PID %OCC_PID%. Choose a different port or stop the process that is using it.
    echo Use: netstat -ano ^| findstr "LISTENING" ^| findstr ":%PORT%"
    endlocal
    goto :EOF
)

%CMD%

endlocal
