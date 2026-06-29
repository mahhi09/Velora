@echo off
setlocal enabledelayedexpansion

REM ============================================
REM  Velora - Task Scheduler Installer
REM  Ye script jis folder me rakha hai, usi folder
REM  me se velora.pyw uthayega aur Task Scheduler
REM  me register karega.
REM ============================================

REM --- Apna folder detect karo ---
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM --- Settings (zaroorat ho to yahan change karo) ---
set "TASK_NAME=Velora"
set "PYTHONW=C:\Users\Mahhi\AppData\Local\Python\bin\pythonw.exe"
set "TARGET=%SCRIPT_DIR%\velora.pyw"
set "RAWFILE=%TEMP%\velora_task_temp_raw.xml"
set "XMLFILE=%TEMP%\velora_task_temp.xml"

REM --- Check: velora.pyw is folder me hai ya nahi ---
if not exist "%TARGET%" (
    echo [ERROR] velora.pyw nahi mila yahan: "%TARGET%"
    echo Please confirm ki velora.pyw isi folder me hai jaha ye .bat file hai.
    pause
    exit /b 1
)

REM --- Check: pythonw.exe maujood hai ya nahi ---
if not exist "%PYTHONW%" (
    echo [WARNING] pythonw.exe nahi mila yahan: "%PYTHONW%"
    echo Agar Python ka path different hai to is script ke PYTHONW variable ko edit karein.
)

REM --- XML generate karo (original settings preserved, sirf paths update) ---
(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.1" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Author^>%COMPUTERNAME%\%USERNAME%^</Author^>
echo     ^<URI^>\%TASK_NAME%^</URI^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<LogonTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo     ^</LogonTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal id="Author"^>
echo       ^<UserId^>%COMPUTERNAME%\%USERNAME%^</UserId^>
echo       ^<LogonType^>InteractiveToken^</LogonType^>
echo       ^<RunLevel^>HighestAvailable^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo     ^<StopIfGoingOnBatteries^>true^</StopIfGoingOnBatteries^>
echo     ^<IdleSettings^>
echo       ^<StopOnIdleEnd^>true^</StopOnIdleEnd^>
echo       ^<RestartOnIdle^>false^</RestartOnIdle^>
echo     ^</IdleSettings^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>true^</Hidden^>
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>
echo     ^<WakeToRun^>false^</WakeToRun^>
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^>
echo     ^<Priority^>7^</Priority^>
echo   ^</Settings^>
echo   ^<Actions Context="Author"^>
echo     ^<Exec^>
echo       ^<Command^>%PYTHONW%^</Command^>
echo       ^<Arguments^>"%TARGET%"^</Arguments^>
echo       ^<WorkingDirectory^>%SCRIPT_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%RAWFILE%"

REM --- ANSI text ko proper UTF-16 encoding me convert karo (schtasks ko UTF-16 chahiye) ---
powershell -NoProfile -Command "$c = Get-Content -LiteralPath '%RAWFILE%' -Raw; [System.IO.File]::WriteAllText('%XMLFILE%', $c, [System.Text.Encoding]::Unicode)"

REM --- Task Scheduler me import karo (output + error log file me bhi save hoga) ---
set "LOGFILE=%SCRIPT_DIR%\velora_install_log.txt"
echo ==== Velora Install Log ==== > "%LOGFILE%"
echo Run time: %DATE% %TIME% >> "%LOGFILE%"
echo SCRIPT_DIR=%SCRIPT_DIR% >> "%LOGFILE%"
echo TARGET=%TARGET% >> "%LOGFILE%"
echo PYTHONW=%PYTHONW% >> "%LOGFILE%"
echo. >> "%LOGFILE%"

if not exist "%XMLFILE%" (
    echo [FAILED] XML encoding convert nahi ho payi - PowerShell error ho sakta hai.
    echo [FAILED] Unicode conversion failed - XMLFILE not created >> "%LOGFILE%"
    del "%RAWFILE%" >nul 2>&1
    echo.
    pause
    exit /b 1
)

schtasks /create /tn "%TASK_NAME%" /xml "%XMLFILE%" /f >> "%LOGFILE%" 2>&1
set "RESULT=%errorlevel%"

if %RESULT% equ 0 (
    echo.
    echo [SUCCESS] Task "%TASK_NAME%" Task Scheduler me successfully add ho gaya!
    echo Target script: %TARGET%
    echo [SUCCESS] >> "%LOGFILE%"
) else (
    echo.
    echo [FAILED] Task add nahi ho paya. Error code: %RESULT%
    echo Is .bat file ko RIGHT-CLICK karke "Run as Administrator" se try karein.
    echo Full error "%LOGFILE%" file me save ho gaya hai - usse open karke dekho.
    echo [FAILED] Error code: %RESULT% >> "%LOGFILE%"
)

del "%XMLFILE%" >nul 2>&1
del "%RAWFILE%" >nul 2>&1

echo.
echo (Pura log yahan bhi hai: %LOGFILE%)
echo.
pause
