Write-Host "Entering .appveyor/install.ps1"
Write-Host "Build using $env:WINPYTHON"
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
    choco install --force --allow-empty-checksums $env:WINPYTHON
    dir C:\ProgramData\chocolatey\bin\python*.exe
    dir c:\python*
}

# Add python and python user-base to path for pip installs
if ($pyVersionSucceeded) {
    $pythonPaths = @(
        "C:\$($env:WINPYTHON)",
        "C:\$($env:WINPYTHON)\Scripts"
    )
} else {
    # If we had to use choco, don't add the potentially missing/broken C:\Python paths
    $pythonPaths = @()
}

# Always add chocolatey bin, but prioritize it if we just installed python there
if (-not $pyVersionSucceeded) {
    $pythonPaths = @("C:\ProgramData\chocolatey\bin") + $pythonPaths
} else {
    $pythonPaths += "C:\ProgramData\chocolatey\bin"
}

# Add tools AFTER python paths to avoid picking up MSYS/Cygwin python shims
$toolPaths = @(
    "C:\MinGW\bin",
    "C:\MinGW\msys\1.0\bin",
    "C:\cygwin\bin",
    "C:\msys64\usr\bin",
    "C:\msys64\mingw64\bin"
)

$env:PATH = ($pythonPaths + $toolPaths + @($env:PATH)) -join ';'
# Ensure we have the correct path to the python executable,
# explicitly avoiding MSYS/Cygwin versions.
$pythonExe = $null

# Derive a version-specific shim name (e.g. Python310 -> python3.10.exe)
$pyVersion = $env:WINPYTHON -replace "Python", "" # e.g. "310"
if ($pyVersion -match "^(\d)(\d+)$") {
    $specName = "python$($Matches[1]).$($Matches[2]).exe" # e.g. "python3.10.exe"
} else {
    $specName = "python.exe"
}

$checkNames = @("$env:WINPYTHON.exe", $specName, "python.exe", "python3.exe")

foreach ($name in $checkNames) {
    Write-Host "Checking for Python shim: $name"
    $cmds = Get-Command $name -ErrorAction SilentlyContinue | Where-Object { $_.Path -notlike "*\msys64\*" -and $_.Path -notlike "*\cygwin\*" }
    if ($cmds) {
        $pythonExe = ($cmds | Select-Object -First 1).Path
        & "$env:SCONS_PYTHON_BIN" --version
        break
    } else {
        Write-Host "Didn't find $name"
    }
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

# pip installs
& $pythonExe -m pip install -U --progress-bar off pip setuptools wheel

# requirements-dev.txt will skip installing lxml for windows and py 3.11+, where there's
# no current binary wheel
& $pythonExe -m pip install -U --progress-bar off -r requirements-dev.txt

choco install --allow-empty-checksums dmd ldc swig vswhere xsltproc winflexbison3

# Show environment variables
Get-ChildItem Env: | Sort-Object Name
Write-Host "Exiting .appveyor/install.ps1"
