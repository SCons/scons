Write-Host "Entering .appveyor/exclude_tests.ps1"
New-Item -Name exclude_list.txt -ItemType File;

# Probe installed MSVS versions for expired/invalid licenses and exclude
# their corresponding tests.
& python testing\ci\check_msvs_licenses.py | ForEach-Object {
    Add-Content -Path 'exclude_list.txt' -Value $_
}

Write-Host "Exiting .appveyor/exclude_tests.ps1"
