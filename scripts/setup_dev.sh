#!/bin/bash
# THIS SCRIPT MUST BE SOURCED
# This script creates a virtual python environment and then links the python
# code in ./src to that virtual environment. The effect is that if you now run
#   sjb-APPNAME-test
# you will run the version of the application given by the local source code.
# This is to allow for local application development without conflicting with
# installation.
DEV_ENV_NAME="venv"
THIS_SCRIPT="scripts/setup_dev.sh"

# Use while loop so we can break out without exiting a sourced script.
while [[ "1" == "1" ]]; do
  # Check that script is sourced.
  if [[ ! $0 =~ /bash$ ]] && [[ ! $0 =~ /sh$ ]] && [[ ! $0 =~ /zsh$ ]]; then
    echo "Error: this script must be sourced (from bash, sh, or zsh)" > /dev/stderr
    break
  fi

  # Ensure we are in the project directory by checking for the '.git'
  if [[ ! -d "$PWD/.git" ]] || [[ ! -f "$PWD/$THIS_SCRIPT" ]]; then
    echo "Error: Please source this script from the project directory" > /dev/stderr
    break
  fi

  # Create virtual environment
  python3.6 -m venv "$DEV_ENV_NAME"
  if [[ "$?" -ne "0" ]]; then break; fi
  source "./$DEV_ENV_NAME/bin/activate"
  if [[ "$?" -ne "0" ]]; then break; fi
  python setup.py install
  if [[ "$?" -ne "0" ]]; then break; fi

  echo "Dev environment setup was successful. To leave type 'deactivate'"
  break
done