#!/bin/bash

python bin/docs-update-generated.py
python bin/docs-validate.py
python bin/docs-create-example-outputs.py
