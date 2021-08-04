#!/usr/bin/env bash
set -x

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    echo "OSX"
    brew install python --framework --universal
else
    # dependencies for clang tests
    sudo apt-get -y install clang

    # setup clang for clang tests using local clang installation
    if [ ! -f /usr/local/clang-5.0.0/bin/clang ]; then
        echo "No Clang 5.0.0 trying 7.0.0"
        sudo ln -s /usr/local/clang-7.0.0/bin/clang /usr/bin/clang
        sudo ln -s /usr/local/clang-7.0.0/bin/clang++ /usr/bin/clang++
    else
        echo "Clang 5.0.0"
        sudo ln -s /usr/local/clang-5.0.0/bin/clang /usr/bin/clang
        sudo ln -s /usr/local/clang-5.0.0/bin/clang++ /usr/bin/clang++
    fi

    # dependencies for rpm packaging tests
    sudo apt-get -y install rpm

    # dependencies for gdc tests
    sudo apt-get -y install gdc

    # dependencies for fortran tests
    sudo apt-get -y install gfortran

    # dependencies for docbook tests
    sudo apt-get -y install docbook-xml docbook-xsl xsltproc libxml2-dev libxslt-dev fop docbook-xsl-doc-pdf
    # docbook-slides should be added but triggers GH #3393 so left out for now.

    # dependencies for latex tests (try to skip the huge doc pkgs)
    sudo apt-get -y --no-install-recommends install texlive texlive-latex3 biber texmaker ghostscript texlive-bibtex-extra texlive-latex-extra texlive-font-utils
    # texlive-latex3 no longer exists, failover to texlive-latex-recommended

    # need some things for building dependencies for other tests
    sudo apt-get -y install python-pip python-dev build-essential libpcre3-dev autoconf automake libtool bison subversion git

    # dependencies for D tests
    sudo wget https://netcologne.dl.sourceforge.net/project/d-apt/files/d-apt.list -O /etc/apt/sources.list.d/d-apt.list
    sudo apt-get update --allow-insecure-repositories
    sudo apt-get -y --allow-unauthenticated install --reinstall d-apt-keyring
    sudo apt-get update && sudo apt-get install dmd-compiler dub


    if [[ "$BUILD_LXML_FROM_GIT" == "1" ]]; then
        pip uninstall -y lxml
        pip cache purge

        # for ubuntu 20.04 needed this as well
        sudo apt install libxslt1-dev

        # then use git versions of cython and lxml (lxml's cython build uses xslt1-config which is why the above was needed)
        pip install git+https://github.com/cython/cython.git@0.29.x
        pip install git+https://github.com/lxml/lxml.git
    fi

#    sudo wget http://master.dl.sourceforge.net/project/d-apt/files/d-apt.list -O /etc/apt/sources.list.d/d-apt.list
#    wget -qO - https://dlang.org/d-keyring.gpg | sudo apt-key add -
#    sudo apt-get update && sudo apt-get -y --allow-unauthenticated install dmd-bin

    # dependencies for ldc tests
    # this install method basically worked until 20.04, though a little messy.
    # rather than further tweaking, replace it with the recommended snap install
    #export SCONS_LDC_VERSION=1.21.0
    #wget https://github.com/ldc-developers/ldc/releases/download/v${SCONS_LDC_VERSION}/ldc2-${SCONS_LDC_VERSION}-linux-x86_64.tar.xz
    #tar xf ldc2-${SCONS_LDC_VERSION}-linux-x86_64.tar.xz
    #sudo cp -rf ldc2-${SCONS_LDC_VERSION}-linux-x86_64/* /
    sudo snap install ldc2 --classic

    # Failing.. ?
#    ls -l /usr/lib*/*python*{so,a}*
fi
