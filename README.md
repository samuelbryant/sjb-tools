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
A "proper" development environment has not been created yet. However, there is 
a crude script which creates s virtual environment. From the main project 
directory:
~~~~
$ . setup_dev.sh
$ . venv/bin/activate
$ pip install sjb-tools
~~~~
You have to rerun the last line every time you change the source code in order 
for it to take effect.

Warning: the development environment still uses the same data files as the real environment. This will eventually be fixed.
