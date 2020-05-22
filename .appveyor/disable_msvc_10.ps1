New-Item -Name exclude_list.txt -ItemType File;
$workaround_image = "Visual Studio 2015";
if ($env:APPVEYOR_BUILD_WORKER_IMAGE -eq $workaround_image) {
    Add-Content -Path 'exclude_list.txt' -Value 'test\MSVS\vs-10.0-exec.py';
}
