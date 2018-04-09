#!/bin/bash
SRC_CODE="../src/"
ERROR_FILE="./errors.txt"
CONFIG_FILE="./pylintrc.config"

find "$SRC_CODE" -name *.py | xargs pylint --rcfile="$CONFIG_FILE" >> "$ERROR_FILE"
cat "$ERROR_FILE"
