#!/usr/bin/env bash

python -m pip install -U coverage codecov

# setup sitecustomize so we can make all subprocess start coverage
export PYSITEDIR=$(python -c "import sys; print(sys.path[-1])")
mkdir -p "$PYSITEDIR"

# coverage.py environment variable for multiprocess
export COVERAGE_PROCESS_START="$PWD/.coveragerc"
export COVERAGE_FILE="$PWD/.coverage"

# replace PWD in the template files so we have absolute paths from out /tmp test folders
sed -e "s#\$PWD#$PWD#" .coverage_templates/.coveragerc.template > "$PWD/.coveragerc"
sed -e "s#\$PWD#$PWD#" .coverage_templates/sitecustomize.py.template > "${PYSITEDIR}/sitecustomize.py"

# print the results
echo "${PYSITEDIR}/sitecustomize.py"
cat "${PYSITEDIR}/sitecustomize.py"
echo "$PWD/.coveragerc"
cat "$PWD/.coveragerc"
