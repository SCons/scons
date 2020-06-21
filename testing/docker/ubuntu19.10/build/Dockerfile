# Building an SCons Release Build image under Ubuntu 19.10
FROM ubuntu:19.10

LABEL version="0.0.1" maintainer="Dirk Baechle <dl9obn@darc.de>" description="SCons Release Build, based on an Ubuntu 19.10"

# Install additional packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install binutils git python3-lxml fop libfontbox-java python3-dev python3-sphinx python3-sphinx-rtd-theme rpm tar curl lynx xterm vim vim-common nano sudo

# Install hyphenation patterns for FOP
RUN mkdir /opt/offo && cd /opt/offo && curl -L --output offo-hyphenation-compiled.zip https://sourceforge.net/projects/offo/files/offo-hyphenation/2.2/offo-hyphenation-compiled.zip/download && unzip offo-hyphenation-compiled.zip && cp offo-hyphenation-compiled/fop-hyph.jar /usr/share/fop/

CMD ["/bin/bash"]
