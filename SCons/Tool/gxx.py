#
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

"""SCons.Tool.g++

Tool-specific initialization for g++.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""


import os, sys
import threading
import asyncio
import atexit
import SCons.Tool
import SCons.Util

from . import gcc
from . import cxx

compilers = ['g++']


def CODY_decode(input):
    quoted = False
    backslashed = False
    result = []
    output = ""

    for c in input:
        if quoted:
            if backslashed:
                output.append(c)
                backslashed = False
                continue
            if c == "'":
                quoted = False
                continue
            if c == "\\":
                backslashed = True
                continue
            output += c
            continue

        if c == "'":
            quoted = True
            continue
        if c == ' ' and output:
            result.append(output)
            output = ""
            continue
        output += c
    if output:
        result.append(output)

    return result


class module_mapper(threading.Thread):
    def __init__(self, env, *args, **kw):
        super().__init__(*args, **kw)
        self.daemon = True
        self.loop = asyncio.new_event_loop()

        self.env = env
        self.load_map()
        atexit.register(self.save_map)

        self.request_dispatch = {}
        self.request_dispatch["HELLO"] = self.hello_response
        self.request_dispatch["INCLUDE-TRANSLATE"] = self.include_translate_response
        self.request_dispatch["MODULE-REPO"] = self.module_repo_response
        self.request_dispatch["MODULE-EXPORT"] = self.module_export_response
        self.request_dispatch["MODULE-COMPILED"] = self.module_compiled_response
        self.request_dispatch["MODULE-IMPORT"] = self.module_import_response

    def save_map(self):
        save = open(self.env.subst("$CXXMODULEPATH/module.map"), "w")

        save.writelines(
            [self.env.subst("$$root $CXXMODULEPATH") + '\n'] +
            [' '.join(pair) + '\n' for pair in self.env["CXXMODULEMAP"].items()])

    def load_map(self):
        try:
            load = open(self.env.subst("$CXXMODULEPATH/module.map"), "r")
        except FileNotFoundError:
            return

        saved_map = dict([tuple(line.rstrip("\n").split(maxsplit=1))
                         for line in load.readlines() if not line[0] == '$'])
        saved_map.update(self.env["CXXMODULEMAP"])
        self.env["CXXMODULEMAP"] = saved_map

    def run(self):
        self.loop.run_forever()

    def hello_response(self, request, sourcefile):
        if(sourcefile != ""):
            return ("ERROR", "'Unexpected handshake'")
        if len(request) == 4 and request[1] == "1":
            return (request[3], "HELLO", "1", "SCONS", "''")
        else:
            return ("ERROR", "'Invalid handshake'")

    def module_repo_response(self, request, sourcefile):
        return ("PATHNAME", self.env["CXXMODULEPATH"])

    def include_translate_response(self, request, sourcefile):
        return ("BOOL", "TRUE")

    def module_export_response(self, request, sourcefile):
        if sourcefile[0] == '@':
            cmi = self.env.subst(sourcefile + "$CXXMODULESUFFIX")
            self.env["CXXMODULEMAP"][request[1]] = cmi
            return ("PATHNAME", cmi)
        else:
            return ("PATHNAME", self.env["CXXMODULEMAP"].get(request[1], self.env.subst(request[1] + "$CXXMODULESUFFIX")))

    def module_compiled_response(self, request, sourcefile):
        return ("OK")

    def module_import_response(self, request, sourcefile):
        return ("PATHNAME", self.env["CXXMODULEMAP"].get(request[1], self.env.subst(request[1] + "$CXXMODULESUFFIX")))

    def default_response(self, request, sourcefile):
        return ("ERROR", "'Unknown CODY request {}'".format(request[0]))

    async def handle_connect(self, reader, writer):
        sourcefile = ""
        while True:
            try:
                request = await reader.readuntil()
            except EOFError:
                return

            request = request.decode("utf-8")

            separator = ''
            request = request.rstrip('\n')
            if request[-1] == ';':
                request = request.rstrip(';')
                separator = ' ;'

            request = CODY_decode(request)

            response = self.request_dispatch.get(
                request[0], self.default_response)(request, sourcefile)
            if(request[0] == "HELLO" and response[0] != "ERROR"):
                sourcefile = response[0]
                response = response[1:]
            response = " ".join(response) + separator + "\n"

            writer.write(response.encode())
            await writer.drain()

    async def listen(self, path):
        if self.env["__GCCMAPPERMODE__"] == "domain_socket":
            await asyncio.start_unix_server(self.handle_connect, path=path)
        else:
            srv = await asyncio.start_server(self.handle_connect, host="::1", port=0)
            self.env["__GCCMAPPERPORT__"] = srv.sockets[0].getsockname()[1]


def init_mapper(env):
    if env.get("__GCCMODULEMAPPER__"):
        return

    mapper = module_mapper(env)
    mapper.start()
    os.makedirs(env.subst("$CXXMODULEPATH"), exist_ok=True)
    asyncio.run_coroutine_threadsafe(mapper.listen(
        env.subst("$CXXMODULEPATH/socket")), mapper.loop)

    env["__GCCMODULEMAPPER__"] = mapper

def generate(env) -> None:
    """Add Builders and construction variables for g++ to an Environment."""
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    if 'CXX' not in env:
        env['CXX'] = env.Detect(compilers) or compilers[0]

    cxx.generate(env)

    # platform specific settings
    if env['PLATFORM'] == 'aix':
        env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS -mminimal-toc')
        env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1
        env['SHOBJSUFFIX'] = '$OBJSUFFIX'
    elif env['PLATFORM'] == 'hpux':
        env['SHOBJSUFFIX'] = '.pic.o'
    elif env['PLATFORM'] == 'sunos':
        env['SHOBJSUFFIX'] = '.pic.o'
    # determine compiler version
    version = gcc.detect_version(env, env['CXX'])
    if version:
        env['CXXVERSION'] = version

    env['CCDEPFLAGS'] = '-MMD -MF ${TARGET}.d'
    env["NINJA_DEPFILE_PARSE_FORMAT"] = 'gcc'

    env['__CXXMODULEINIT__'] = init_mapper
    if sys.platform != "win32":
        env['__GCCMAPPERMODE__'] = "domain_socket"
        env['__GCCMAPPERFLAGS__'] = "=$CXXMODULEPATH/socket"
    else:
        env['__GCCMAPPERMODE__'] = "tcp"
        env['__GCCMAPPERFLAGS__'] = "::1:$($__GCCMAPPERPORT__$)"
    env['CXXMODULEFLAGS'] = '-fmodules-ts -fmodule-mapper=$__GCCMAPPERFLAGS__?$CXXMODULEIDPREFIX$SOURCE'
    env['CXXMODULESUFFIX'] = '.gcm'
    env['CXXUSERHEADERFLAGS']    = '-x c++-user-header'
    env['CXXSYSTEMHEADERFLAGS']  = '-x c++-system-header'


def exists(env):
    # is executable, and is a GNU compiler (or accepts '--version' at least)
    return gcc.detect_version(env, env.Detect(env.get('CXX', compilers)))
