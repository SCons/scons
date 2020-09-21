dir "C:\Program Files\Git\usr\bin\x*.exe";
if (Test-Path "C:\Program Files\Git\usr\bin\xsltproc.EXE" ) {
    Remove-Item  "C:\Program Files\Git\usr\bin\xsltproc.EXE" -ErrorAction Ignore;
}
dir "C:\Program Files\Git\usr\bin\x*.exe";
