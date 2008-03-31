#!/bin/sh
#
# A script for unpacking and installing different historic versions of
# SCons in a consistent manner for side-by-side development testing.
#
# This abstracts the changes we've made to the SCons setup.py scripts in
# different versions so that, no matter what version is specified, it ends
# up install the necessary script(s) and library into version-specific
# names that won't interfere with other things.
#
# We expect to extract the .tar.gz files from a Downloads subdirectory
# in the current directory.
#
# Note that this script cleans up after itself, removing the extracted
# directory in which we do the build.
#
# This was written for a Linux system (specifically Ubuntu) but should
# be reasonably generic to any POSIX-style system with a /usr/local
# hierarchy.

USAGE="\
Usage: $0 [-ahnq] [-d DIR] [-p PREFIX] [VERSION ...]
"

PRINT="echo"
EXECUTE="eval"

DOWNLOADS=Downloads
DOWNLOADS_URL=http://downloads.sourceforge.net/scons
SUDO=sudo
PREFIX=/usr/local

while getopts "ad:hnq" FLAG; do
    case ${FLAG} in
    a )
        ALL="1"
        ;;
    d )
        DOWNLOADS="${OPTARG}"
        ;;
    h )
        echo "${USAGE}"
        exit 0
        ;;
    n )
        EXECUTE=":"
        ;;
    p )
        PREFIX="${OPTARG}"
        ;;
    q )
        PRINT=":"
        ;;
    * )
        echo "$0: unknown option ${FLAG}; use -h for help." >&2
        exit 1
        ;;
    esac
done

shift `expr ${OPTIND} - 1`

VERSIONS="$*"

if test "X${ALL}" != "X"; then
    if test "${VERSIONS}"; then
        msg="$0:  -a and version arguments both specified on the command line"
        echo "${msg}" >&2
        exit 1
    fi
    VERSIONS="
    0.01
    0.02
    0.03
    0.04
    0.05
    0.06
    0.07
    0.08
    0.09
    0.10
    0.11
    0.12
    0.13
    0.14
    0.90
    0.91
    0.92
    0.93
    0.94
    0.94.1
    0.95
    0.95.1
    0.96
    0.96.1
    0.96.90
    0.96.91
    0.96.92
    0.96.93
    0.96.94
    0.96.95
    0.96.96
    0.97
    0.97.0d20070809
    0.97.0d20070918
    0.97.0d20071212
    "
fi

Command()
{
    ${PRINT} "$*"
    ARGS=`echo "$*" | sed 's/\\$/\\\\$/'`
    ${EXECUTE} "$*"
}

for VERSION in $VERSIONS; do
    SCONS=scons-${VERSION}

    TAR_GZ=${SCONS}.tar.gz
    if test ! -f ${DOWNLOADS}/${TAR_GZ}; then
        if test ! -d ${DOWNLOADS}; then
            Command mkdir ${DOWNLOADS}
        fi
        Command "( cd ${DOWNLOADS} && wget ${DOWNLOADS_URL}/${TAR_GZ} )"
    fi

    Command tar zxf ${DOWNLOADS}/${TAR_GZ}

    (
        Command cd ${SCONS}

        case ${VERSION} in
        0.0[123456789] | 0.10 )
            # 0.01 through 0.10 install /usr/local/bin/scons and
            # /usr/local/lib/scons.  The "scons" script knows how to
            # look up the library in a version-specific directory, but
            # we have to move both it and the library directory into
            # the right version-specific name by hand.
            Command python setup.py build
            Command ${SUDO} python setup.py install --prefix=${PREFIX}
            Command ${SUDO} mv ${PREFIX}/bin/scons ${PREFIX}/bin/scons-${VERSION}
            Command ${SUDO} mv ${PREFIX}/lib/scons ${PREFIX}/lib/scons-${VERSION}
            ;;
        0.1[1234] | 0.90 )
            # 0.11 through 0.90 install /usr/local/bin/scons and
            # /usr/local/lib/scons-${VERSION}.  We just need to move
            # the script to a version-specific name.
            Command python setup.py build
            Command ${SUDO} python setup.py install --prefix=${PREFIX}
            Command ${SUDO} mv ${PREFIX}/bin/scons ${PREFIX}/bin/scons-${VERSION}
            ;;
        0.9[123456] | 0.9[456].1 | 0.96.90 )
            # 0.91 through 0.96.90 install /usr/local/bin/scons,
            # /usr/local/bin/sconsign and /usr/local/lib/scons-${VERSION}.
            # We need to move both scripts to version-specific names.
            Command python setup.py build
            Command ${SUDO} python setup.py install --prefix=${PREFIX}
            Command ${SUDO} mv ${PREFIX}/bin/scons ${PREFIX}/bin/scons-${VERSION}
            Command ${SUDO} mv ${PREFIX}/bin/sconsign ${PREFIX}/bin/sconsign-${VERSION}
            if test -d ${PREFIX}/lib/scons; then
                Command ${SUDO} mv ${PREFIX}/lib/scons ${PREFIX}/lib/scons-${VERSION}
            fi
            ;;
        * )
            # Versions from 0.96.91 and later (through at least 0.97)
            # support what we want with a --no-scons-script option.
            Command python setup.py build
            Command ${SUDO} python setup.py install --prefix=${PREFIX} --no-scons-script
            ;;
        esac

        ${PRINT} cd ..
    )
    Command rm -rf ${SCONS}
done
