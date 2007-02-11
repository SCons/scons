@REM __COPYRIGHT__
@REM __FILE__ __REVISION__ __DATE__ __DEVELOPER__
@echo off
if "%OS%" == "Windows_NT" goto WinNT
REM for 9x/Me you better not have more than 9 args
python -c "from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-__VERSION__'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons-__VERSION__'), join(sys.prefix, 'scons')] + sys.path; import SCons.Script; SCons.Script.main()" %1 %2 %3 %4 %5 %6 %7 %8 %9
@REM no way to set exit status of this script for 9x/Me
goto endscons
:WinNT
set path=%path%;%~dp0
python -c "from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-__VERSION__'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons-__VERSION__'), join(sys.prefix, 'scons')] + sys.path; import SCons.Script; SCons.Script.main()" %*
if NOT "%COMSPEC%" == "%SystemRoot%\system32\cmd.exe" goto endscons
if errorlevel 9009 echo you do not have python in your PATH
@REM color 00 causes this script to exit with non-zero exit status
if errorlevel 1 color 00
:endscons
