#!/bin/bash

# Source code directory
SRC_DIR="./src"
SRC_TEST_DIR="./test"

# All of sjb project suites
OTHER_PROJECTS=("../sjb_cheatsheet" "../sjb_calendar")

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
rm "$LINT_ERRORS"
find "$SRC_DIR" -name *.py | xargs pylint --rcfile="$LINT_CONFIG" >> "$LINT_ERRORS"
# Compare lint errors to benchmark file
diff "$LINT_ERRORS" "$LINT_BENCHMARK"
if [[ "$?" -ne "0" ]]; then
  failure "Project lint did not match benchmark"
fi
# Make sure project lint config matches other project configs
for project in ${OTHER_PROJECTS[@]}; do
	diff "$LINT_CONFIG" "$project/$LINT_CONFIG"
	if [[ "$?" -ne "0" ]]; then
  		failure "Lint config out of sync with other projects"
	fi
done



echo "Everything seems okay"
exit 0
