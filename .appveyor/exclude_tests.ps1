New-Item -Name exclude_list.txt -ItemType File;

# exclude VS 10.0 because it hangs the testing until this is resolved:
# https://help.appveyor.com/discussions/problems/19283-visual-studio-2010-trial-license-has-expired
$workaround_image = "Visual Studio 2015";
if ($env:APPVEYOR_BUILD_WORKER_IMAGE -eq $workaround_image) {
    Add-Content -Path 'exclude_list.txt' -Value 'test\MSVS\vs-10.0-exec.py';
}
