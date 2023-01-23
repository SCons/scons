C:\\%WINPYTHON%\\python.exe --version
for /F "tokens=*" %%g in ('C:\\%WINPYTHON%\\python.exe -c "import sys; print(sys.path[-1])"') do (set PYSITEDIR=%%g)
REM use mingw 32 bit until #3291 is resolved
REM add python and python user-base to path for pip installs
set PATH=C:\\%WINPYTHON%;C:\\%WINPYTHON%\\Scripts;C:\\ProgramData\\chocolatey\\bin;C:\\MinGW\\bin;C:\\MinGW\\msys\\1.0\\bin;C:\\cygwin\\bin;C:\\msys64\\usr\\bin;C:\\msys64\\mingw64\\bin;%PATH%
C:\\%WINPYTHON%\\python.exe -m pip install -U --progress-bar off pip setuptools wheel
REM No real use for lxml on Windows (and some versions don't have it):
REM We don't install the docbook bits so those tests won't run anyway
REM The Windows builds don't attempt to make the docs
REM Adjust this as requirements-dev.txt changes.
REM C:\\%WINPYTHON%\\python.exe -m pip install -U --progress-bar off -r requirements-dev.txt
C:\\%WINPYTHON%\\python.exe -m pip install -U --progress-bar off ninja psutil
choco install --allow-empty-checksums dmd ldc swig vswhere xsltproc winflexbison3
set
