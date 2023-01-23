for /F "tokens=*" %%g in ('C:\\%WINPYTHON%\\python.exe -c "import sys; print(sys.path[-1])"') do (set PYSITEDIR=%%g)
C:\\%WINPYTHON%\\python.exe -m pip install -U --progress-bar off coverage codecov
