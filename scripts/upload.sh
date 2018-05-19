#!/bin/bash

# Go to project directory
cd "$(dirname "$0")/.."

# Get the version
version=$(./scripts/get_version.sh)

echo "The version tag is '$version'"
echo "git describe gives '$(git describe)'"
echo "Do you wish to continue? (y/n): "
read resp
if [[ ! $resp =~ ^[yY](e|es)?$ ]]; then
  exit 0
fi

if [[ "$1" -eq "-n" ]]; then
  echo "Deploying version $version to pypi (dry run)"
  echo "python3 setup.py sdist upload --dry-run"
  #python3 setup.py sdist upload --dry-run
else
  echo "Deploying version $version to pypi"
  echo "python3 setup.py sdist upload"
  python3 setup.py sdist upload
fi