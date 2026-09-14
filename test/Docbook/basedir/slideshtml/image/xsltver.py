# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import os
import re

re_version = re.compile(b"<fm:Version>([^<]+)</fm:Version>")
re_branch = re.compile(b"<fm:Branch>([^<]+)</fm:Branch>")

# Lowest version the callers treat as namespace-aware. Used as a stand-in when
# VERSION names the XSL-NS branch but carries a non-numeric version string.
NS_VERSION = (1, 78, 0)

def detectXsltVersion(fpath):
    """ Return a tuple with the version of the Docbook XSLT stylesheets,
        or (0, 0, 0) if no stylesheets are found or the VERSION
        file couldn't be found/parsed correctly.

        Not every distribution puts a number in <fm:Version>: Debian and
        Ubuntu's docbook-xsl 1.79.2 ships "snapshot" there. Callers only
        use the result to decide whether the stylesheets are namespace
        aware, and <fm:Branch> states that outright, so fall back to it
        instead of reporting (0, 0, 0) - which would feed the plain,
        non-namespaced input to namespace-aware stylesheets and quietly
        produce an empty document.
    """
    try:
        with open(os.path.join(fpath, 'VERSION'), 'rb') as fin:
            content = fin.read()
    except OSError:
        return (0, 0, 0)

    m = re_version.search(content)
    if m:
        try:
            return tuple(map(int, m.group(1).split(b'.')))
        except ValueError:
            pass

    m = re_branch.search(content)
    if m and b'XSL-NS' in m.group(1):
        return NS_VERSION

    return (0, 0, 0)
