"""SCons.Tool.DCommon

Common code for the various D tools.

Coded by Russel Winder (russel@winder.org.uk)
2012-09-06
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

import os.path

def isD(source):
    if not source:
        return 0
    for s in source:
        if s.sources:
            ext = os.path.splitext(str(s.sources[0]))[1]
            if ext == '.d':
                return 1
    return 0

def addDPATHToEnv(env, executable):
    dPath = env.WhereIs(executable)
    if dPath:
        phobosDir = dPath[:dPath.rindex(executable)] + '/../src/phobos'
        if os.path.isdir(phobosDir):
            env.Append(DPATH=[phobosDir])

def setSmartLink(env, smart_link, smart_lib):
    linkcom = env.get('LINKCOM')
    try:
        env['SMART_LINKCOM'] = smart_link[linkcom]
    except KeyError:
        def _smartLink(source, target, env, for_signature, defaultLinker=linkcom):
            if isD(source):
                # TODO: I'm not sure how to add a $DLINKCOMSTR variable
                # so that it works with this _smartLink() logic,
                # and I don't have a D compiler/linker to try it out,
                # so we'll leave it alone for now.
                return '$DLINKCOM'
            else:
                return defaultLinker
        env['SMART_LINKCOM'] = smart_link[linkcom] = _smartLink

    arcom = env.get('ARCOM')
    try:
        env['SMART_ARCOM'] = smart_lib[arcom]
    except KeyError:
        def _smartLib(source, target, env, for_signature, defaultLib=arcom):
            if isD(source):
                # TODO: I'm not sure how to add a $DLIBCOMSTR variable
                # so that it works with this _smartLib() logic, and
                # I don't have a D compiler/archiver to try it out,
                # so we'll leave it alone for now.
                return '$DLIBCOM'
            else:
                return defaultLib
        env['SMART_ARCOM'] = smart_lib[arcom] = _smartLib

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
