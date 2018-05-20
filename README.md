# sjb-tools
A set of simple command line productivity tools.

This project is licensed under the MIT license.

Currently there are two tools: a todo list (sjb-todo) and a cheatsheet
(sjb-cheatsheet). Each of these programs allows the user to create, read,
update, and delete (CRUD) new entries from the command line. These are
designed to be simple and transparent replacements for common producitivity
tools (like Apple's reminders).

Currently there is only a command line interface that interacts with local
data. Eventually I plan to have these talk to other services and will maybe
build a command line.


# Installation
Assuming you have python3.X and `pip3` installed on your system:
~~~~
# pip install sjb-tools
~~~~

# Usage
See `sjb-cheatsheet --help` and `sjb-todo --help` for usage. This file is not
kept up to date.

# Developing
I have not adopted a proper development environment framework yet. However, I
have setup a few very useful scripts.

To setup the development environment, `cd` into the project directory and type:
~~~~
$ . scripts/setup_dev.sh
~~~~
All this does is create the development environment. It does **not** activate that environment. To activate the development environment, type:
~~~~
$ dev-env-on
~~~~
To install the program into the test environment, test:
~~~~
$ python setup.py install
~~~~
Finally, to exit the development environment, type:
~~~~
$ dev-env-off
~~~~
**Note** You have to re-run `python setup.py install` every time you make
changes to the source code.

These scripts are basically just a wrapper around a python `virtualenv` that
set some environment variables to let the program know it is running in test.

If you want to make changes or contribute to the source code, contact me.
