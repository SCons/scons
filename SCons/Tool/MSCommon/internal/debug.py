"""
Debug logging for working with the Microsoft tool chain.
"""
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

from .config import _MSCONFIG

if _MSCONFIG.DEBUG_STDOUT:

    def debug(message):
        print(message)

elif _MSCONFIG.DEBUG_LOGGING:

    import logging

    modulelist = (
        # root module and parent/root module
        'MSCommon', 'Tool',
        # python library and below: correct iff scons does not have a lib folder
        'lib',
        # scons modules
        'SCons', 'test', 'scons'
    )

    class _Debug_Filter(logging.Filter):
        # custom filter for module relative filename
        def filter(self, record):
            relfilename = _MSCONFIG.get_relative_filename(record.pathname, modulelist)
            relfilename = relfilename.replace('\\', '/')
            record.relfilename = relfilename
            return True

    logging.basicConfig(
        # This looks like:
        #   00109ms:MSCommon/vc.py:find_vc_pdir#447:
        format=(
            '%(relativeCreated)05dms'
            ':%(relfilename)s'
            ':%(funcName)s'
            '#%(lineno)s'
            ':%(message)s: '
        ),
        filename=_MSCONFIG.rewrite_filename(_MSCONFIG.DEBUG_LOGFILE, sync=False),
        level=logging.DEBUG)

    logger = logging.getLogger(name=__name__)
    logger.addFilter(_Debug_Filter())
    debug = logger.debug

else:

    def debug(message):
        return None

