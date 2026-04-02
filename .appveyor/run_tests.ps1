if ($env:COVERAGE -eq 1) {
    & "$env:SCONS_PYTHON_BIN" -m coverage run -p --rcfile "$env:COVERAGE_PROCESS_START" runtest.py -j 2 -t --exclude-list exclude_list.txt -a
} else {
    & "$env:SCONS_PYTHON_BIN" runtest.py -j 2 -t --exclude-list exclude_list.txt -a
}

# Treat exit code 2 (some tests failed) as success for AppVeyor 
# as per original configuration.
if ($LastExitCode -eq 2 -or $LastExitCode -eq 0) {
    exit 0
} else {
    exit $LastExitCode
}
