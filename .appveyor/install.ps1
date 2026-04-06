Write-Host "Entering .appveyor/install.ps1"
$pythonExe = "C:\$($env:WINPYTHON)\python.exe"

# If the initial call to python --version fails, call "choco install %WINPYTHON%"
$pyVersionSucceeded = $false
try {
    if (Test-Path $pythonExe) {
        & $pythonExe --version
        if ($LASTEXITCODE -eq 0) {
            $pyVersionSucceeded = $true
        }
    }
} catch {
    $pyVersionSucceeded = $false
}

if (-not $pyVersionSucceeded) {
    Write-Host "Python version check failed or Python not found at $pythonExe. Installing $env:WINPYTHON via Chocolatey..."
    choco install --allow-empty-checksums $env:WINPYTHON
}

# Ensure we have the correct path to the python executable
if (Get-Command $env:WINPYTHON -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command $env:WINPYTHON).Path
} elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command python.exe).Path
}

if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    Write-Error "Could not find a valid Python executable (WINPYTHON=$env:WINPYTHON). Aborting."
    exit 1
}

Write-Host "Using Python at: $pythonExe"

Write-Host "PATH: $env:PATH"

# Set SCONS_PYTHON_BIN for future steps
Set-AppveyorBuildVariable -Name "SCONS_PYTHON_BIN" -Value "$pythonExe"

# Set PYSITEDIR
$env:PYSITEDIR = & $pythonExe -c "import sys; print(sys.path[-1])"
Set-AppveyorBuildVariable -Name "PYSITEDIR" -Value "$env:PYSITEDIR"

# Use mingw 32 bit until #3291 is resolved
# Add python and python user-base to path for pip installs
$extraPaths = @(
    "C:\$($env:WINPYTHON)",
    "C:\$($env:WINPYTHON)\Scripts",
    "C:\ProgramData\chocolatey\bin",
    "C:\MinGW\bin",
    "C:\MinGW\msys\1.0\bin",
    "C:\cygwin\bin",
    "C:\msys64\usr\bin",
    "C:\msys64\mingw64\bin"
)
$env:PATH = ($extraPaths + @($env:PATH)) -join ';'

# pip installs
& $pythonExe -m pip install -U --progress-bar off pip setuptools wheel

# requirements-dev.txt will skip installing lxml for windows and py 3.11+, where there's
# no current binary wheel
& $pythonExe -m pip install -U --progress-bar off -r requirements-dev.txt

choco install --allow-empty-checksums dmd ldc swig vswhere xsltproc winflexbison3

# Show environment variables
Get-ChildItem Env: | Sort-Object Name
Write-Host "Exiting .appveyor/install.ps1"
