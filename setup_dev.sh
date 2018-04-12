#!/bin/bash
# THIS SCRIPT MUST BE SOURCED
# This script creates a virtual python environment and then links the python
# code in ./src to that virtual environment. The effect is that if you now run
#   sjb-APPNAME-test
# you will run the version of the application given by the local source code.
# This is to allow for local application development without conflicting with
# installation.

echo "This script must be sourced"

FRONTEND_NAME="sjb-todo"
DEV_ENV_NAME="venv"

# Create virtual environment.
python3.6 -m venv "$DEV_ENV_NAME"
source "./$DEV_ENV_NAME/bin/activate"
if [ -e "$PWD/$DEV_ENV_NAME/lib/python3.6/site-packages/sjb" ]; then
  rm "$PWD/$DEV_ENV_NAME/lib/python3.6/site-packages/sjb"
fi
ln -s "$PWD/src/sjb" "$PWD/$DEV_ENV_NAME/lib/python3.6/site-packages/sjb"

# Put testing binary into bin
cp "./bin/$FRONTEND_NAME" "$DEV_ENV_NAME/bin/$FRONTEND_NAME"
