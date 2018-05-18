#!/bin/bash
# Library settings
## Machine install location
#DEFAULT_LIB_LOCATION="/usr/local/lib/python3.6/dist-packages"

SUITE_LIB_NAME="sjb"
APP_LIB_NAME="td"
COMMON_LIB_NAME="common"
FRONTEND_NAME="sjb-todo"

# Library install locations
SITE_LIB_LOC="/usr/local/lib/python3.6/dist-packages"
USER_LIB_LOC="$HOME/.local/lib/python3.6/site-packages"

# Frontend settings
SITE_FRONTEND_TARGET="/usr/local/bin/${FRONTEND_NAME}"
USER_FRONTEND_TARGET="$HOME/bin/${FRONTEND_NAME}"

# Local sources
local_frontend="./bin/${FRONTEND_NAME}"
local_suite_lib="./src/$SUITE_LIB_NAME"
local_app_lib="./src/$SUITE_LIB_NAME/$APP_LIB_NAME"
local_common_lib="./src/$SUITE_LIB_NAME/$COMMON_LIB_NAME"

RED='\033[0;41m'
NC='\033[0m' # No Color

function wrnmsg {
  echo -e "${RED}Warning:${NC} $1" > /dev/stderr
}

function errmsg {
  echo -e "${RED}Error:${NC} $1" > /dev/stderr
}

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

# Check that local sources exist.
if [ ! -f "$local_frontend" ]; then
  errmsg "Local frontend script not found: '$local_frontend'"
  exit 1
elif [ ! -d "$local_suite_lib" ]; then
  errmsg "Local suite library not found: '$local_suite_lib'"
  exit 1
elif [ ! -d "$local_app_lib" ]; then
  errmsg "Local app library not found: '$local_app_lib'"
  exit 1
elif [ ! -d "$local_common_lib" ]; then
  errmsg "Local common library not found: '$local_common_lib'"
  exit 1
fi

# Prompt user to get library install location.
printf "Where would you like to install the python libraries?\n"
printf "\t1 (user) ${USER_LIB_LOC}\n"
printf "\t2 (site) ${SITE_LIB_LOC}\n"
read -p "Choose (default is 1): " choice
if [[ "$choice" == "1" ]] || [[ "$choice" == "" ]]; then
  lib_location="${USER_LIB_LOC}"
  lib_is_sitewide=0
elif [[ "$choice" == "2" ]]; then
  lib_location="${SITE_LIB_LOC}"
  lib_is_sitewide=1
else
  errmsg "Bad response"
  exit 1
fi

# Prompt user to get binary install location
printf "Where would you like to install the frontend script?\n"
printf "\t1 (user) ${USER_FRONTEND_TARGET}\n"
printf "\t2 (site) ${SITE_FRONTEND_TARGET}\n"
read -p "Choose (default is 2): " choice
if [[ "$choice" == "1" ]]; then
  frontend_target="${USER_FRONTEND_TARGET}"
  frontend_is_sitewide=0
elif [[ "$choice" == "2" ]] || [[ "$choice" == "" ]]; then
  frontend_target="${SITE_FRONTEND_TARGET}"
  frontend_is_sitewide=1
else
  errmsg "Bad response"
  exit 1
fi

target_suite_lib="${lib_location}/$SUITE_LIB_NAME"
target_app_lib="${lib_location}/$SUITE_LIB_NAME/$APP_LIB_NAME"
target_common_lib="${lib_location}/$SUITE_LIB_NAME/$COMMON_LIB_NAME"
flag_copy_common_lib=1
flag_remove_old_app_lib=0
flag_remove_old_common_lib=0

# Check that install directory exists:
if [ ! -d "${lib_location}" ]; then
  errmsg "Error: Install directory does not exist! ('${lib_location}')"
  exit 1
fi

# Check that install directory is in the python library path:
python3.6 -c "import sys; sys.exit('${lib_location}' not in sys.path)"
if [ "$?" -ne "0" ]; then
  errmsg "Error: Install directory ('${lib_location}') was not found in python path (sys.path)"
  exit 1
fi

# Check if app library is already installed
if [ -e "$target_app_lib" ]; then
  wrnmsg "previous install found. Overwriting..."
  flag_remove_old_app_lib=1
fi

# Check if common library is already installed and matches this library.
if [ -e "$target_common_lib" ]; then
  diff -r "$local_common_lib" "$target_common_lib" 1>/dev/null 2>/dev/null
  if [ "$?" -ne "0" ]; then
    #wrnmsg "common lib mismatch: '${local_common_lib}' vs '${target_common_lib}'"
    wrnmsg "the target common library is already installed but its contents are different from the common library you are trying to install. If you overwrite it, it is possible it will break another $SUITE_LIB_NAME application."
    read -p "Would you like to remove the old common library and replace it with the new one? (y/N) " resp
    if [[ $resp =~ ^[yY](e|es)?$ ]]; then
      flag_remove_old_common_lib=1
      flag_copy_common_lib=1
    elif [[ $resp =~ ^[nN][oO]?$ ]] || [[ "$resp" == "" ]]; then
      exit 0
    else
      errmsg "Bad response"
      exit 1
    fi
  else
    flag_copy_common_lib=0
  fi
fi


########## END OF CHECKS START OF CHANGES #####################

# Create suite library directory
if [[ "$lib_is_sitewide" != "0" ]]; then
  sudo mkdir -p "$target_suite_lib"
else
  mkdir -p "$target_suite_lib"
fi
if [ "$?" -ne "0" ]; then
  errmsg "Something went wrong with creating the suite library"
  exit 1
fi

# Remove old common library if required
if [[ "$flag_remove_old_common_lib" ]]; then
  if [[ "$lib_is_sitewide" != "0" ]]; then
    sudo rm -rf "$target_common_lib"
  else
    rm -rf "$target_common_lib"
  fi
  if [ "$?" -ne "0" ]; then
    errmsg "Something went wrong while removing old common lib. It is likely that the $SUITE_LIB_NAME applications may be in a broken state. Sorry."
    exit 2
  fi
fi

# Remove old app library if required
if [[ "$flag_remove_old_app_lib" -eq "1" ]]; then
  if [[ "$lib_is_sitewide" != "0" ]]; then
    sudo rm -rf "$target_app_lib"
  else
    rm -rf "$target_app_lib"
  fi
  if [ "$?" -ne "0" ]; then
    errmsg "Something went wrong while removing old app lib. It is likely that the application is in a broken state. Sorry."
    exit 2
  fi
fi

# Copy common library
if [[ "$flag_copy_common_lib" -eq "1" ]]; then
  if [[ "$lib_is_sitewide" != "0" ]]; then
    sudo cp -r "$local_common_lib" "$target_common_lib"
  else
    cp -r "$local_common_lib" "$target_common_lib"
  fi
  if [ "$?" -ne "0" ]; then
    errmsg "Something went wrong while copying common lib. It is likely that the application is in a broken state. Sorry."
    exit 2
  fi
fi

# Copy app library
if [[ "$lib_is_sitewide" != "0" ]]; then
  sudo cp -r "$local_app_lib" "$target_app_lib" 
else
  cp -r "$local_app_lib" "$target_app_lib" 
fi
if [ "$?" -ne "0" ]; then
  errmsg "Something went wrong while copying app lib. It is likely that the application is in a broken state. Sorry."
  exit 2
fi

# Copy frontend script
if [[ "$frontend_is_sitewide" != "0" ]]; then
  sudo cp "$local_frontend" "$frontend_target"
else
  cp "$local_frontend" "$frontend_target"
fi
if [ "$?" -ne "0" ]; then
  errmsg "Something went wrong while copying frontend script. It is likely that the application is in a broken state. Sorry."
  exit 2
fi

echo "Installation was a success!"
