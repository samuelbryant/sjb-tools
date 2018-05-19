#!/bin/bash
#     This script checks that the hard-coded project version in sjb/
# constants.py matches the project version returned by 'git describe'. It
# returns the following:
#  0: If the git and project versions match
#  1: If the git and project versions dont match
#  2: If the git or project versions do not follow expected conventions (or
#     the version getting scripts are broken.)
#
# This accepts a single option '--quiet' which will surpress error messages.
#
#     There is one major subtlety that you should be aware of: 'git describe'
# returns number of revisions from the *last* release tag. However, the
# project version convention is to indicate the number of revisions preparing
# for the *next* release tag. e.g.:
#  git describe --> 1.2.4-7-151lk3j  # means 7 revisions since tag 1.2.4
#  project ver  --> 1.2.5.dev7   # means 7 revisions since version 1.2.4
# There is some inherent ambiguity here because 'git describe' is agnostic to
# what the next release will be. e.g. 1.2.4-7-43143 does not indicate if the
# next release will be 1.2.5 or 1.3.0.
#     This script assumes that the next release *always* increments the micro
# version, i.e. that 1.2.4 will always be followed by 1.2.5. TODO: in the
# future, I should write a more sophisticated tool that can handle minor/major
# version number changes.

if [[ "$1" == "--quiet" ]]; then
  flag_quiet="1"
elif [[ "$#" -ne "0" ]]; then
  echo "Incorrect usage" > /dev/stderr
  echo "Usage: $0 [--quiet]" > /dev/stderr
  exit 3
else
  flag_quiet="0"
fi

function errmsg {
  if [[ "$flag_quiet" == "0" ]]; then
    echo "Error: $1" > /dev/stderr
  fi
}
function assert_equal {
  if [[ "$1" != "$2" ]]; then
    errmsg "$3"
    exit 1
  fi
}

# Go to project directory
cd "$(dirname "$0")/.."

gver=$(git describe)
pver=$(./scripts/get_version.sh)

# First check that the versions are formatted correctly
if [[ ! $gver =~ ^[0-9]+\.[0-9]+\.[0-9]+(\-[0-9]+\-[a-z0-9]+)?$ ]]; then
  errmsg "git version '$gver' did not match expected regex"
  exit 2
elif [[ ! $pver =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.dev[0-9]+)?$ ]]; then
  errmsg "project version '$pver' did not match expected regex"
  exit 2
fi

# Next extract the components of each version tag
gparts=($(echo "$gver" | sed -E 's/([0-9]+)\.([0-9]+)\.([0-9]+)(\-([0-9]+)\-.*)?/\1 \2 \3 \5/g'))
pparts=($(echo "$pver" | sed -E 's/([0-9]+)\.([0-9]+)\.([0-9]+)(\.dev([0-9]+))?/\1 \2 \3 \5/g'))

# If this is not a development version, just make sure the parts match
if [[ "${gparts[3]}" == "" ]]; then
  assert_equal "${gparts[0]}" "${pparts[0]}" "the major versions did not match '$gver' vs '$pver'"
  assert_equal "${gparts[1]}" "${pparts[1]}" "the minor versions did not match '$gver' vs '$pver'"
  assert_equal "${gparts[2]}" "${pparts[2]}" "the micro versions did not match '$gver' vs '$pver'"
  assert_equal "${gparts[3]}" "${pparts[3]}" "the devel versions did not match '$gver' vs '$pver'"
else
  # TODO: This currently wont work for minor version updates.
  assert_equal "${gparts[0]}" "${pparts[0]}" "the major versions did not match '$gver' vs '$pver'"
  assert_equal "${gparts[1]}" "${pparts[1]}" "the minor versions did not match '$gver' vs '$pver'"
  # For development version, the git tag should be one behind since it counts revisions *after* the last tag but the dev counts *before* release
  gmic="${gparts[2]}"
  ((testmicro=$gmic + 1))
  assert_equal "$testmicro" "${pparts[2]}" "the micro versions did not match '$gver' vs '$pver'"
  assert_equal "${gparts[3]}" "${pparts[3]}" "the devel versions did not match '$gver' vs '$pver'"
fi

exit 0
