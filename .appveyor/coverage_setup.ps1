if ($env:COVERAGE -eq 1) {
    $env:COVERAGE_PROCESS_START = "$($env:APPVEYOR_BUILD_FOLDER)\.coveragerc";
    $env:COVERAGE_FILE = "$($env:APPVEYOR_BUILD_FOLDER)\.coverage";
    New-Item -ItemType Directory -Force -Path "$($env:PYSITEDIR)";

    (Get-Content -path .coverage_templates\.coveragerc.template -Raw) -replace '\$PWD',"$((Get-Location) -replace '\\', '/')" | Set-Content -Path "$($env:COVERAGE_PROCESS_START)";
    (Get-Content -path .coverage_templates\sitecustomize.py.template -Raw) -replace '\$PWD',"$((Get-Location) -replace '\\', '/')" | Set-Content -Path "$($env:PYSITEDIR)\sitecustomize.py";

    Write-Host "$($env:PYSITEDIR)\sitecustomize.py";
    Get-Content -Path "$($env:PYSITEDIR)\sitecustomize.py";
    Write-Host "$($env:COVERAGE_PROCESS_START)";
    Get-Content -Path "$($env:COVERAGE_PROCESS_START)";
}
