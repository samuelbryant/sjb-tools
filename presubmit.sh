#!/bin/bash
set -u

# Source code directory
SRC_DIR="src"

# Code that should be same between projects
COMMON_CODE="./src/sjb/common"

# All of sjb project suites
ALL_PROJECTS=("../sjb_cheatsheet" "../sjb_calendar" "../sjb_todo")

# Lint directory
LINT_DIR="./lint"
# Lint benchmark file
LINT_BENCHMARK="$LINT_DIR/errors_benchmark.txt"
# Lint error file
LINT_ERRORS="$LINT_DIR/errors.txt"
# Lint config file
LINT_CONFIG="$LINT_DIR/pylintrc.config"

failure() {
  echo "Presubmit Failed: $1" >> /dev/stderr
  exit 1
}

## Lint project
echo "Checking lint status..."
pylint --rcfile="$LINT_CONFIG" "$SRC_DIR" > "$LINT_ERRORS"
#find "$SRC_DIR" -name *.py | xargs pylint --ignore=experimental --rcfile="$LINT_CONFIG" >> "$LINT_ERRORS"
# Compare lint errors to benchmark file
diff "$LINT_ERRORS" "$LINT_BENCHMARK" > /dev/null
if [[ "$?" -ne "0" ]]; then
  failure "Project lint did not match benchmark"
fi
# Make sure project lint config matches other project configs
for project in ${ALL_PROJECTS[@]}; do
	diff "$LINT_CONFIG" "$project/$LINT_CONFIG" 1> /dev/null
	if [[ "$?" -ne "0" ]]; then
  		failure "Lint config out of sync with other projects"
	fi
done


## Compare common code across projects
echo "Checking that common python libraries are in sync..."
for project in ${ALL_PROJECTS[@]}; do
  diff "$COMMON_CODE" "$project/$COMMON_CODE" 1> /dev/null
  if [[ "$?" -ne "0" ]]; then
      failure "Common code out of sync between files"
  fi
done

echo "Everything seems okay"
exit 0
