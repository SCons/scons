# This script makes it possible to run a test without building first
export PYTHONPATH="`pwd`/src:`pwd`/etc"
python $1
