if ($env:COVERAGE -eq 1) {
    & coverage combine;
    & coverage report;
    & coverage xml -i -o coverage_xml.xml;
}
