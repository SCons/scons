#!/bin/sh

# Here we can add local setup steps for the finishing touches to our Docker build container.
# This can be setting symbolic links, e.g.
#   sudo ln -s /disk2/stuff /stuff
# or triggering further scripts.

# We start a separate xterm/terminal, such that the container doesn't exit right away...
/usr/bin/xterm

