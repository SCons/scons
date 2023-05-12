# MIT License
#
# Copyright The SCons Foundation
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

"""SCons.Tool.DCommon

Common code for the various D tools.

Coded by Russel Winder (russel@winder.org.uk)
2012-09-06
"""
import SCons.Util

import os.path

def isD(env, source) -> int:
    if not source:
        return 0
    for s in source:
        if s.sources:
            ext = os.path.splitext(str(s.sources[0]))[1]
            if ext == '.d':
                return 1
    return 0


def addDPATHToEnv(env, executable) -> None:
    dPath = env.WhereIs(executable)
    if dPath:
        phobosDir = dPath[:dPath.rindex(executable)] + '/../src/phobos'
        if os.path.isdir(phobosDir):
            env.Append(DPATH=[phobosDir])


def allAtOnceEmitter(target, source, env):
    if env['DC'] in ('ldc2', 'dmd'):
        env.SideEffect(str(target[0]) + '.o', target[0])
        env.Clean(target[0], str(target[0]) + '.o')
    return target, source

def _optWithIxes(pre,x,suf,env,f=lambda x: x, target=None, source=None) -> str:
# a single optional argument version of _concat
#    print ("_optWithIxes",str(target),str(source))
    if x in env:
        l = f(SCons.PathList.PathList([env[x]]).subst_path(env, target, source))
        return pre + str(l[0]) + suf
    else:
        return ""

def DObjectEmitter(target,source,env):
    if "DINTFDIR" in env:
        if (len(target) != 1):
            raise Exception("expect only one object target")
        targetBase, targetName = os.path.split(SCons.Util.to_String(target[0]))
        extraTarget = os.path.join(targetBase,str(env["DINTFDIR"]),targetName[:-len(env["OBJSUFFIX"])] + env["DIFILESUFFIX"])
        target.append(extraTarget)
    return (target,source)

def DStaticObjectEmitter(target,source,env):
    for tgt in target:
        tgt.attributes.shared = None
    return DObjectEmitter(target,source,env)

def DSharedObjectEmitter(target,source,env):
    for tgt in target:
        tgt.attributes.shared = 1
    return DObjectEmitter(target,source,env)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
