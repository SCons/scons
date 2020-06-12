# Building an SCons Test image under Fedora 32
FROM fedora:32

LABEL version="0.0.1" maintainer="Dirk Baechle <dl9obn@darc.de>" description="SCons Test image, based on a Fedora 32"

# Install additional packages
RUN dnf -y install git bison cvs flex g++ gcc ghostscript m4 openssh-clients openssh-server python3-line_profiler python3-devel pypy3-devel rpm-build rcs java-1.8.0-openjdk swig texlive-scheme-basic texlive-base texlive-latex zip xterm vim vim-common nano

CMD ["/bin/bash"]

