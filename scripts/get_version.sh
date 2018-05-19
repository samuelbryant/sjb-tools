#!/bin/bash

version=$(cat sjb/constants.py | grep 'version' | sed -E 's/__version__ ?= ?'"'"'(.*)'"'"'/\1/g')

echo "$version"