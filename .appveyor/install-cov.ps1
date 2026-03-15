$pythonExe = "C:\$($env:WINPYTHON)\python.exe"
$env:PYSITEDIR = & $pythonExe -c "import sys; print(sys.path[-1])"
& $pythonExe -m pip install -U --progress-bar off coverage codecov
