# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import os
import re

def detectXsltVersion(fpath):
    """ Return a tuple with the version of the Docbook XSLT stylesheets,
        or (0, 0, 0) if no stylesheets are found or the VERSION
        file couldn't be found/parsed correctly.
    """
    with open(os.path.join(fpath, 'VERSION'), 'rb') as fin:
        re_version = re.compile(b"<fm:Version>([^<]+)</fm:Version>")
        m = re_version.search(fin.read())
        if m:
            try:
                return tuple(map(int, m.group(1).split(b'.')))
            except Exception:
                return (0, 0, 0)

        return (0, 0, 0)

    return (0, 0, 0)
