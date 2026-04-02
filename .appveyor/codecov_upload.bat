@echo off
if "%COVERAGE%"=="1" (
    "%SCONS_PYTHON_BIN%" -m codecov -X gcov --file coverage_xml.xml
)
