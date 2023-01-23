C:\\%WINPYTHON%\\python.exe --version
for /F "tokens=*" %%g in ('C:\\%WINPYTHON%\\python.exe -c "import sys; print(sys.path[-1])"') do (set PYSITEDIR=%%g)
REM use mingw 32 bit until #3291 is resolved
REM add python and python user-base to path for pip installs
set PATH=C:\\%WINPYTHON%;C:\\%WINPYTHON%\\Scripts;C:\\ProgramData\\chocolatey\\bin;C:\\MinGW\\bin;C:\\MinGW\\msys\\1.0\\bin;C:\\cygwin\\bin;C:\\msys64\\usr\\bin;C:\\msys64\\mingw64\\bin;%PATH%
C:\\%WINPYTHON%\\python.exe -m pip install -U --progress-bar off pip setuptools wheel

REM requirements-dev.txt will skip installing lxml for windows and py 3.11+, where there's
REM no current binary wheel
C:\\%WINPYTHON%\\python.exe -m pip install -U --progress-bar off -r requirements-dev.txt

choco install --allow-empty-checksums dmd ldc swig vswhere xsltproc winflexbison3
set
