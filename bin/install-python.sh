#!/bin/sh
#
# A script for unpacking and installing different historic versions of
# Python in a consistent manner for side-by-side development testing.
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
DOWNLOADS_URL=http://www.python.org/ftp/python
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
    1.5.2
    2.0.1
    2.1.3
    2.2
    2.3.6
    2.4.4
    "
    # 2.5.1
fi

Command()
{
    ${PRINT} "$*"
    ARGS=`echo "$*" | sed 's/\\$/\\\\$/'`
    ${EXECUTE} "$*"
}

for VERSION in $VERSIONS; do
    PYTHON=Python-${VERSION}

    TAR_GZ=${PYTHON}.tgz
    if test ! -f ${DOWNLOADS}/${TAR_GZ}; then
        if test ! -d ${DOWNLOADS}; then
            Command mkdir ${DOWNLOADS}
        fi
        Command "( cd ${DOWNLOADS} && wget ${DOWNLOADS_URL}/${VERSION}/${TAR_GZ} )"
    fi

    Command tar zxf ${DOWNLOADS}/${TAR_GZ}

    (
        Command cd ${PYTHON}

        case ${VERSION} in
        1.5* )
            CONFIGUREFLAGS="--with-threads"
            ;;
        1.6* | 2.0* )
            # Add the zlib module so we get zipfile compression.
            Command ed Modules/Setup.in <<EOF
/^#zlib/s/#//
w
q
EOF
            CONFIGUREFLAGS="--with-threads"
            ;;
        esac

        Command ./configure --prefix=${PREFIX} ${CONFIGUREFLAGS} 2>&1 | tee configure.out
        Command make 2>&1 | tee make.out
        Command ${SUDO} make install

        Command ${SUDO} rm -f ${PREFIX}/bin/{idle,pydoc,python,python-config,smtpd.py}

        ${PRINT} cd ..
    )

    Command rm -rf ${Python}
done
