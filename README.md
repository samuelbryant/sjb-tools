# sjb_todo
A simple CRUD command line program for working with 'todo lists'

This project is licensed under the MIT license.

# Installation
This program is in pre-alpha and is not using any deployment tools so I make zero guarantees about installation.

However, I have written a crude script that should more or less work provided the user has `python3.6` installed in a linux environment and has all of the required python dependencies. Since these dependencies are subject to change, and this is my first time writing a deployed python app, I have not bothered to record them or incorporate them into the install script. In the future I hope to fix this.

## Instructions
~~~~
$ cd <this directory>
$ ./install.sh
$ mkdir -p ~/.local/share/sjb/todo
~~~~
where `<this directory>` is the directory containing this README file. Also it's important that you run `./install.sh` as a regular user (dont use sudo).

# Developing
There is a script `setup_dev.sh` which sets up a virtual environment. This causes `sjb-todo` to execute the local code in `src` instead of the code installed on the system.

To enter the development environment:
~~~
$ cd <this directory>
$ . setup_dev.sh
~~~
where `<this directory>` is the directory containing this README file.

To leave the development environment just type:
~~~~
$ deactivate
~~~~

Warning: the development environment still uses the same data files as the real environment. This will eventually be fixed.
