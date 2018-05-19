# THIS SCRIPT MUST BE SOURCED
# This script creates a virtual python environment and then links the python
# code in ./src to that virtual environment. The effect is that if you now run
#   sjb-APPNAME-test
# you will run the version of the application given by the local source code.
# This is to allow for local application development without conflicting with
# installation.
DEV_ENV_NAME="venv"
THIS_SCRIPT="scripts/setup_dev.sh"
TEST_XDG_DATA_HOME_RELATIVE="venv/home/user/.local/share"
TEST_XDG_CONFIG_HOME_RELATIVE="venv/home/user/.config"


# These functions serve as pseudo-scripts we can call to turn the test
# environment on/off
function dev-env-on {
  echo "Turning dev environment on for project at '$_PROJECT_DIR'"
  . "$_PROJECT_DIR/$DEV_ENV_NAME/bin/activate"
  # Setup environment variables
  export SJB_TOOLS_TEST=1
  export TEST_XDG_DATA_HOME="$_PROJECT_DIR/$TEST_XDG_DATA_HOME_RELATIVE"
  export TEST_XDG_CONFIG_HOME="$_PROJECT_DIR/$TEST_XDG_CONFIG_HOME_RELATIVE"
  echo "to exit dev environment: dev-env-off"
}

function dev-env-off {
  echo "Turning dev environment off for project at '$_PROJECT_DIR'"
  deactivate
  # Setup environment variables
  unset SJB_TOOLS_TEST
  unset TEST_XDG_DATA_HOME
  unset TEST_XDG_CONFIG_HOME
  echo "to re-enter dev environment: dev-env-on"
}

# Use while loop so we can break out without exiting a sourced script.
flag_success="0"
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
  _PROJECT_DIR="$PWD"

  # Create virtual environment
  python3.6 -m venv "$DEV_ENV_NAME"
  if [[ "$?" -ne "0" ]]; then break; fi

  # Setup git development hooks.
  echo "Setting up git hooks"
  ./scripts/setup_git_hooks
  if [[ "$?" -ne "0" ]]; then break; fi

  flag_success="1"
  break
done

if [[ "$flag_success" -eq "1" ]]; then
  echo "Dev environment setup was successful."
  echo "to enter dev environment: dev-env-on"
  echo "to leave dev environment: dev-env-off"
  echo "to install project: python setup.py install"
  echo "Warning: Don't use 'activate' or 'deactivate'"
  true # set $? to 0
else
  echo "Something went wrong while setting up the dev environment" > /dev/stderr
  false # set $? to 1
fi