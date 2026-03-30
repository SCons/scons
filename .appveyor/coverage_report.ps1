if ($env:COVERAGE -eq 1) {
    & $env:SCONS_PYTHON_BIN -m coverage combine;
    & $env:SCONS_PYTHON_BIN -m coverage report;
    & $env:SCONS_PYTHON_BIN -m coverage xml -i -o coverage_xml.xml;
}
