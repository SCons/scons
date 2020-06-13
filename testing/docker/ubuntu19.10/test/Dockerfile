# Building an SCons Test image under Ubuntu 19.10
FROM ubuntu:19.10

LABEL version="0.0.1" maintainer="Dirk Baechle <dl9obn@darc.de>" description="SCons Test image, based on an Ubuntu 19.10"

# Install additional packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install git bison cssc cvs flex g++ gcc ghostscript m4 openssh-client openssh-server python3-profiler python3-all-dev pypy-dev rcs rpm openjdk-8-jdk swig texlive-base-bin texlive-extra-utils texlive-latex-base texlive-latex-extra zip xterm vim vim-common nano sudo

CMD ["/bin/bash"]

