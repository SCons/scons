# Building an SCons Release Build image under Ubuntu 19.10
FROM ubuntu:19.10

LABEL version="0.0.1" maintainer="Dirk Baechle <dl9obn@darc.de>" description="SCons Release Build, based on an Ubuntu 19.10"

# Install additional packages
RUN apt-get update && apt-get -y install git python3-lxml fop libfontbox-java python3-dev rpm tar curl lynx xterm vim vim-common nano sudo

# Install hyphenation patterns for FOP
RUN mkdir /opt/offo && cd /opt/offo && curl -L --output offo-hyphenation-compiled.zip https://sourceforge.net/projects/offo/files/offo-hyphenation/2.2/offo-hyphenation-compiled.zip/download && unzip offo-hyphenation-compiled.zip && cp offo-hyphenation-compiled/fop-hyph.jar /usr/share/fop/

# Epydoc can be installed via pip3, but it doesn't seem to work properly.
# For the moment we don't install it and might replace it with Sphinx later...
# RUN apt-get -y install python3-pip && pip3 install epydoc

CMD ["/bin/bash"]

