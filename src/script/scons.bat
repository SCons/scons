@echo off
if "%OS%" == "Windows_NT" goto WinNT
REM for 9x/Me you better not have more than 9 args
python -c "import SCons.Script; SCons.Script.main()" %1 %2 %3 %4 %5 %6 %7 %8 %9
REM no way to set exit status of this script for 9x/Me
goto endscons
:WinNT
python -c "import SCons.Script; SCons.Script.main()" %*
if NOT "%COMSPEC%" == "%SystemRoot%\system32\cmd.exe" goto endscons
if errorlevel 9009 echo you do not have python in your PATH
REM color 00 causes this script to exit with non-zero exit status
if errorlevel 1 color 00
:endscons
