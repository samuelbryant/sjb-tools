#!/bin/bash
# Library settings
## Machine install location
#DEFAULT_LIB_LOCATION="/usr/local/lib/python3.6/dist-packages"
## Local install location (use until ready for prod)
DEFAULT_LIB_LOCATION="$HOME/.local/lib/python3.6/site-packages"
SUITE_LIB_NAME="sjb"
APP_LIB_NAME="td"
COMMON_LIB_NAME="common"

# Frontend settings
TARGET_FRONTEND_SCRIPT="/usr/local/bin/sjb-todo"
LOCAL_FRONTEND_SCRIPT="./bin/sjb-todo.py"

# Make sure we are not running as sudo user:
if [ "$EUID" -eq 0 ]; then
  echo "Error: script cannot be run as root (dont use sudo)"
  exit 1
fi

# Check that python3.6 is installed
python3.6 --version 2>/dev/null 1>/dev/null
if [ "$?" -ne "0" ]; then
  echo "Error: python3.6 not found. Make sure its installed first"
  exit 2
fi

# Prompt user for the python library location
printf "Enter library directory intall directory (default is ${DEFAULT_LIB_LOCATION}): "
read location
if [[ "$location"=="" ]]; then
  location="$DEFAULT_LIB_LOCATION"
fi

# Check that install directory is in the python library path:
python3.6 -c "import sys; sys.exit('$location' not in sys.path)"
if [ "$?" -ne "0" ]; then
  echo "Error: Install directory ('$location') was not found in python path (sys.path)"
fi

# Check that install directory exists:
if [ ! -d "$location" ]; then
  echo "Error: Install directory does not exist! ('$location')"
  exit 1
fi

target_suite_lib="$location/$SUITE_LIB_NAME"
target_app_lib="$location/$SUITE_LIB_NAME/$APP_LIB_NAME"
target_common_lib="$location/$SUITE_LIB_NAME/$COMMON_LIB_NAME"
local_suite_lib="./src/$SUITE_LIB_NAME"
local_app_lib="./src/$SUITE_LIB_NAME/$APP_LIB_NAME"
local_common_lib="./src/$SUITE_LIB_NAME/$COMMON_LIB_NAME"

# Create suite library directory
sudo mkdir -p "$target_suite_lib"

flag_copy_common_lib=1
flag_remove_old_app_lib=0

# Check that local sources exist.
if [ ! -f "$LOCAL_FRONTEND_SCRIPT" ]; then
  echo "Error: Local frontend script not found: '$LOCAL_FRONTEND_SCRIPT'"
  exit 1
elif [ ! -d "$local_suite_lib" ]; then
  echo "Error: Local suite library not found: '$local_suite_lib'"
  exit 1
elif [ ! -d "$local_app_lib" ]; then
  echo "Error: Local app library not found: '$local_app_lib'"
  exit 1
elif [ ! -d "$local_common_lib" ]; then
  echo "Error: Local common library not found: '$local_common_lib'"
  exit 1
fi

# Check if common library is already installed and matches this library.
if [ -e "$target_common_lib" ]; then
  diff "$local_common_lib" "$target_common_lib" 1>/dev/null 2>/dev/null
  if [ "$?" -ne "0" ]; then
    echo "Error: target common library is already installed (at '$target_common_lib') but its contents are different from the common library you are trying to install (at '$local_common_lib')"
    echo "This likely means you have previously installed a different version of some '$SUITE_LIB_NAME' app. Currently this upgrade script cannot handle this scenario and the common library is not guaranteed to be backwards compatible. I will fix this in the future."
    echo "Goodbye."
    exit 1
  fi
  flag_copy_common_lib=0
fi

# Check if app library is already installed
if [ -e "$target_app_lib" ]; then
  echo "Warning: previous install found. Overwriting..."
  flag_remove_old_app_lib=1
fi


# All checks done. Time to actually do stuff
if [[ "$flag_copy_common_lib" -eq "1" ]]; then
  sudo cp -r "$local_common_lib" "$target_common_lib"
fi
if [[ "$flag_remove_old_app_lib" -eq "1" ]]; then
  sudo rm -r "$target_app_lib"
fi
sudo cp -r "$local_app_lib" "$target_app_lib" 
sudo cp "$LOCAL_FRONTEND_SCRIPT" "$TARGET_FRONTEND_SCRIPT"

echo "Installation was a success!"
