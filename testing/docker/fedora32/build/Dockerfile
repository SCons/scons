# Building an SCons Release Build image under Fedora 32
FROM fedora:32

LABEL version="0.0.1" maintainer="Dirk Baechle <dl9obn@darc.de>" description="SCons Release Build, based on a Fedora 32"

# Install additional packages
RUN dnf -y install git python3-lxml binutils fop fontbox python3-devel python3-sphinx python3-sphinx_rtd_theme lynx xterm vim vim-common nano unzip

# Install hyphenation patterns for FOP
RUN mkdir /opt/offo && cd /opt/offo && curl -L --output offo-hyphenation-compiled.zip https://sourceforge.net/projects/offo/files/offo-hyphenation/2.2/offo-hyphenation-compiled.zip/download && unzip offo-hyphenation-compiled.zip && cp offo-hyphenation-compiled/fop-hyph.jar /usr/share/fop/

# Epydoc can be installed via pip3, but it doesn't seem to work properly.
# For the moment we don't install it and might replace it with Sphinx later...
# RUN dnf -y install python3-pip && pip3 install epydoc

CMD ["/bin/bash"]

