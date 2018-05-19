#!/bin/bash
# THIS SCRIPT MUST BE SOURCED
# This script creates a virtual python environment and then links the python
# code in ./src to that virtual environment. The effect is that if you now run
#   sjb-APPNAME-test
# you will run the version of the application given by the local source code.
# This is to allow for local application development without conflicting with
# installation.

echo "This script must be sourced"

DEV_ENV_NAME="venv"

python3.6 -m venv "$DEV_ENV_NAME"
source "./$DEV_ENV_NAME/bin/activate"
python setup.py install
