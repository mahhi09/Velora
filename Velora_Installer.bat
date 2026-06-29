@echo off
title Velora Installer
setlocal enabledelayedexpansion

set "SRC=%~dp0"
set "SRC=%SRC:~0,-1%"
set "DEST=%APPDATA%\Velora"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\velora.lnk"

echo ============================================
echo  Installing Velora...
echo  Source     : %SRC%
echo  Destination: %DEST%
echo ============================================
echo.

if not exist "%DEST%" mkdir "%DEST%"

REM --- STEP 1: Move everything except this installer file ---
echo [1/3] Moving files...
robocopy "%SRC%" "%DEST%" /E /MOVE /XF "%~nx0" /NFL /NDL /NJH /NJS >nul

if not exist "%DEST%\velora.pyw" (
    echo [ERROR] velora.pyw not found after move. Aborting.
    dir "%DEST%"
    pause
    exit /b 1
)
echo     Done.
echo.

REM --- STEP 2: Install requirements.txt if present ---
echo [2/3] Checking for requirements.txt...
if exist "%DEST%\requirements.txt" (
    where python >nul 2>nul
    if errorlevel 1 (
        echo     [WARNING] Python not found, skipping pip install.
    ) else (
        echo     Installing packages...
        python -m pip install -r "%DEST%\requirements.txt" >nul 2>nul
        echo     Done.
    )
) else (
    echo     No requirements.txt found, skipping.
)
echo.

REM --- STEP 3: Create Startup shortcut (target = pythonw.exe, arg = full script path, start in = script folder) ---
echo [3/3] Creating Startup shortcut...
set "PYTHONW="
for /f "delims=" %%P in ('where pythonw 2^>nul') do set "PYTHONW=%%P"

if "%PYTHONW%"=="" (
    echo [ERROR] pythonw.exe not found. Make sure Python is installed and added to PATH.
    pause
    exit /b 1
)

powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%PYTHONW%'; $s.Arguments='\"%DEST%\velora.pyw\"'; $s.WorkingDirectory='%DEST%'; $s.Save()"

if not exist "%SHORTCUT%" (
    echo [ERROR] Shortcut creation failed.
    pause
    exit /b 1
)
echo     Done.
echo.

echo ============================================
echo  Installation successful!
echo  Velora will start silently on next login.
echo ============================================
echo.
echo Cleaning up installer in 3 seconds...
timeout /t 3 /nobreak >nul

REM --- Self-delete: remove the now-empty source folder (which only contains this .bat) ---
start /min cmd /c "timeout /t 2 /nobreak >nul & rmdir /s /q "%SRC%""
exit
