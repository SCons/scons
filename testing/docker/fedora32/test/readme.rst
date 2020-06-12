=======================
Image for testing SCons
=======================

This folder contains the files and scripts that can be used to
test SCons, based on a Fedora 32.

Building the image
==================

Build the local docker image by calling::

    ./build_image.sh
    
This will download the base image and install the required additional packages.

Starting the image
==================

Is done via ``docker-compose`` so make sure you have this package installed in your host system. Then call::

    ./start_test_shell.sh

which will open a new ``xterm`` with your current user on the host system as default.

If you need additional setup steps or want to *mount* different folders to the test image, change the
files::

    docker-compose.yml
    ./startup/setup_container.sh

locally.


Stopping the image
==================

Simply call::

    ./stop_test_shell.sh

.

