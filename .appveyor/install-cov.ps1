Write-Host "Entering .appveyor/install-cov.ps1"
if ($env:COVERAGE -eq 1) {
    $pythonExe = $env:SCONS_PYTHON_BIN
    $env:PYSITEDIR = & $pythonExe -c "import sys; print(sys.path[-1])"
    & $pythonExe -m pip install -U --progress-bar off coverage codecov
}
Write-Host "Exiting .appveyor/install-cov.ps1"
