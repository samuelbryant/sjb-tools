#!/bin/bash

# Go to project directory
cd "$(dirname "$0")/.."

# Get the version
version=$(cat sjb/constants.py | grep 'version' | sed -E 's/__version__ ?= ?'"'"'(.*)'"'"'/\1/g')

echo "The version tag is '$version'"
echo "git describe gives '$(git describe)'"
echo "Do you wish to continue? (y/n): "
read resp
if [[ ! $resp =~ ^[yY](e|es)?$ ]]; then
  exit 0
fi

echo "deploying version $version to pypi"
python3 setup.py sdist upload
