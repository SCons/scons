# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
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

import io
import os
import pathlib
import signal
import tempfile
import shutil
import sys
import random
import filecmp
from os.path import splitext
from tempfile import NamedTemporaryFile
import ninja
import hashlib

import SCons
from SCons.Script import COMMAND_LINE_TARGETS
from SCons.Util import wait_for_process_to_die
from SCons.Errors import InternalError
from .Globals import COMMAND_TYPES, NINJA_RULES, NINJA_POOLS, \
    NINJA_CUSTOM_HANDLERS, NINJA_DEFAULT_TARGETS
from .Rules import _install_action_function, _mkdir_action_function, _lib_symlink_action_function, _copy_action_function
from .Utils import get_path, alias_to_ninja_build, generate_depfile, ninja_noop, get_order_only, \
    get_outputs, get_inputs, get_dependencies, get_rule, get_command_env, to_escaped_list, ninja_sorted_build
from .Methods import get_command


# pylint: disable=too-many-instance-attributes
class NinjaState:
    """Maintains state of Ninja build system as it's translated from SCons."""

    def __init__(self, env, ninja_file, ninja_syntax):
        self.env = env
        self.ninja_file = ninja_file

        self.ninja_bin_path = env.get('NINJA')
        if not self.ninja_bin_path:
            # default to using ninja installed with python module
            ninja_bin = 'ninja.exe' if env["PLATFORM"] == "win32" else 'ninja'
            self.ninja_bin_path = os.path.abspath(os.path.join(
                ninja.__file__,
                os.pardir,
                'data',
                'bin',
                ninja_bin))
            if not os.path.exists(self.ninja_bin_path):
                # couldn't find it, just give the bin name and hope
                # its in the path later
                self.ninja_bin_path = ninja_bin
        self.ninja_syntax = ninja_syntax
        self.writer_class = ninja_syntax.Writer
        self.__generated = False
        self.translator = SConsToNinjaTranslator(env)
        self.generated_suffixes = env.get("NINJA_GENERATED_SOURCE_SUFFIXES", [])

        # List of generated builds that will be written at a later stage
        self.builds = dict()

        # SCons sets this variable to a function which knows how to do
        # shell quoting on whatever platform it's run on. Here we use it
        # to make the SCONS_INVOCATION variable properly quoted for things
        # like CCFLAGS
        scons_escape = env.get("ESCAPE", lambda x: x)

        # The daemon port should be the same across runs, unless explicitly set
        # or if the portfile is deleted. This ensures the ninja file is deterministic
        # across regen's if nothings changed. The construction var should take preference,
        # then portfile is next, and then otherwise create a new random port to persist in
        # use.
        scons_daemon_port = None
        os.makedirs(get_path(self.env.get("NINJA_DIR")), exist_ok=True)
        scons_daemon_port_file = str(pathlib.Path(get_path(self.env.get("NINJA_DIR"))) / "scons_daemon_portfile")

        if env.get('NINJA_SCONS_DAEMON_PORT') is not None:
            scons_daemon_port = int(env.get('NINJA_SCONS_DAEMON_PORT'))
        elif os.path.exists(scons_daemon_port_file):
            with open(scons_daemon_port_file) as f:
                scons_daemon_port = int(f.read())
        else:
            scons_daemon_port = random.randint(10000, 60000)

        with open(scons_daemon_port_file, 'w') as f:
            f.write(str(scons_daemon_port))

        # if SCons was invoked from python, we expect the first arg to be the scons.py
        # script, otherwise scons was invoked from the scons script
        python_bin = ''
        if os.path.basename(sys.argv[0]) == 'scons.py':
            python_bin = ninja_syntax.escape(scons_escape(sys.executable))
        self.variables = {
            "COPY": "cmd.exe /c 1>NUL copy" if sys.platform == "win32" else "cp",
            'PORT': scons_daemon_port,
            'NINJA_DIR_PATH': env.get('NINJA_DIR').abspath,
            'PYTHON_BIN': sys.executable,
            'NINJA_TOOL_DIR': pathlib.Path(__file__).parent,
            'NINJA_SCONS_DAEMON_KEEP_ALIVE': str(env.get('NINJA_SCONS_DAEMON_KEEP_ALIVE')),
            "SCONS_INVOCATION": '{} {} --disable-ninja __NINJA_NO=1 $out'.format(
                python_bin,
                " ".join(
                    [ninja_syntax.escape(scons_escape(arg)) for arg in sys.argv if arg not in COMMAND_LINE_TARGETS]
                ),
            ),
            "SCONS_INVOCATION_W_TARGETS": "{} {} NINJA_DISABLE_AUTO_RUN=1".format(
                python_bin, " ".join([
                    ninja_syntax.escape(scons_escape(arg))
                    for arg in sys.argv
                    if arg != 'NINJA_DISABLE_AUTO_RUN=1'])
            ),
            # This must be set to a global default per:
            # https://ninja-build.org/manual.html#_deps
            # English Visual Studio will have the default below,
            # otherwise the user can define the variable in the first environment
            # that initialized ninja tool
            "msvc_deps_prefix": env.get("NINJA_MSVC_DEPS_PREFIX", "Note: including file:")
        }

        self.rules = {
            "CMD": {
                "command": "cmd /c $env$cmd $in $out" if sys.platform == "win32" else "$env$cmd $in $out",
                "description": "Building $out",
                "pool": "local_pool",
            },
            "GENERATED_CMD": {
                "command": "cmd /c $env$cmd" if sys.platform == "win32" else "$env$cmd",
                "description": "Building $out",
                "pool": "local_pool",
            },
            # We add the deps processing variables to this below. We
            # don't pipe these through cmd.exe on Windows because we
            # use this to generate a compile_commands.json database
            # which can't use the shell command as it's compile
            # command.
            "CC_RSP": {
                "command": "$env$CC @$out.rsp",
                "description": "Compiling $out",
                "rspfile": "$out.rsp",
                "rspfile_content": "$rspc",
            },
            "CXX_RSP": {
                "command": "$env$CXX @$out.rsp",
                "description": "Compiling $out",
                "rspfile": "$out.rsp",
                "rspfile_content": "$rspc",
            },
            "LINK_RSP": {
                "command": "$env$LINK @$out.rsp",
                "description": "Linking $out",
                "rspfile": "$out.rsp",
                "rspfile_content": "$rspc",
                "pool": "local_pool",
            },
            # Ninja does not automatically delete the archive before
            # invoking ar. The ar utility will append to an existing archive, which
            # can cause duplicate symbols if the symbols moved between object files.
            # Native SCons will perform this operation so we need to force ninja
            # to do the same. See related for more info:
            # https://jira.mongodb.org/browse/SERVER-49457
            "AR_RSP": {
                "command": "{}$env$AR @$out.rsp".format(
                    '' if sys.platform == "win32" else "rm -f $out && "
                ),
                "description": "Archiving $out",
                "rspfile": "$out.rsp",
                "rspfile_content": "$rspc",
                "pool": "local_pool",
            },
            "CC": {
                "command": "$env$CC $rspc",
                "description": "Compiling $out",
            },
            "CXX": {
                "command": "$env$CXX $rspc",
                "description": "Compiling $out",
            },
            "LINK": {
                "command": "$env$LINK $rspc",
                "description": "Linking $out",
                "pool": "local_pool",
            },
            "AR": {
                "command": "{}$env$AR $rspc".format(
                    '' if sys.platform == "win32" else "rm -f $out && "
                ),
                "description": "Archiving $out",
                "pool": "local_pool",
            },
            "SYMLINK": {
                "command": (
                    "cmd /c mklink $out $in"
                    if sys.platform == "win32"
                    else "ln -s $in $out"
                ),
                "description": "Symlink $in -> $out",
            },
            "INSTALL": {
                "command": "$COPY $in $out",
                "description": "Install $out",
                "pool": "install_pool",
                # On Windows cmd.exe /c copy does not always correctly
                # update the timestamp on the output file. This leads
                # to a stuck constant timestamp in the Ninja database
                # and needless rebuilds.
                #
                # Adding restat here ensures that Ninja always checks
                # the copy updated the timestamp and that Ninja has
                # the correct information.
                "restat": 1,
            },
            "TEMPLATE": {
                "command": "$PYTHON_BIN $NINJA_TOOL_DIR/ninja_daemon_build.py $PORT $NINJA_DIR_PATH $out",
                "description": "Defer to SCons to build $out",
                "pool": "local_pool",
                "restat": 1
            },
            "EXIT_SCONS_DAEMON": {
                "command": "$PYTHON_BIN $NINJA_TOOL_DIR/ninja_daemon_build.py $PORT $NINJA_DIR_PATH --exit",
                "description": "Shutting down ninja scons daemon server",
                "pool": "local_pool",
                "restat": 1
            },
            "SCONS": {
                "command": "$SCONS_INVOCATION $out",
                "description": "$SCONS_INVOCATION $out",
                "pool": "scons_pool",
                # restat
                #    if present, causes Ninja to re-stat the command's outputs
                #    after execution of the command. Each output whose
                #    modification time the command did not change will be
                #    treated as though it had never needed to be built. This
                #    may cause the output's reverse dependencies to be removed
                #    from the list of pending build actions.
                #
                # We use restat any time we execute SCons because
                # SCons calls in Ninja typically create multiple
                # targets. But since SCons is doing it's own up to
                # date-ness checks it may only update say one of
                # them. Restat will find out which of the multiple
                # build targets did actually change then only rebuild
                # those targets which depend specifically on that
                # output.
                "restat": 1,
            },

            "SCONS_DAEMON": {
                "command": "$PYTHON_BIN $NINJA_TOOL_DIR/ninja_run_daemon.py $PORT $NINJA_DIR_PATH $NINJA_SCONS_DAEMON_KEEP_ALIVE $SCONS_INVOCATION",
                "description": "Starting scons daemon...",
                "pool": "local_pool",
                # restat
                #    if present, causes Ninja to re-stat the command's outputs
                #    after execution of the command. Each output whose
                #    modification time the command did not change will be
                #    treated as though it had never needed to be built. This
                #    may cause the output's reverse dependencies to be removed
                #    from the list of pending build actions.
                #
                # We use restat any time we execute SCons because
                # SCons calls in Ninja typically create multiple
                # targets. But since SCons is doing it's own up to
                # date-ness checks it may only update say one of
                # them. Restat will find out which of the multiple
                # build targets did actually change then only rebuild
                # those targets which depend specifically on that
                # output.
                "restat": 1,
            },
            "REGENERATE": {
                "command": "$SCONS_INVOCATION_W_TARGETS",
                "description": "Regenerating $self",
                "generator": 1,
                "pool": "console",
                "restat": 1,
            },
        }

        if env['PLATFORM'] == 'darwin' and env.get('AR', "") == 'ar':
            self.rules["AR"] = {
                "command": "rm -f $out && $env$AR $rspc",
                "description": "Archiving $out",
                "pool": "local_pool",
            }
        self.pools = {"scons_pool": 1}

    def add_build(self, node):
        if not node.has_builder():
            return False

        if isinstance(node, SCons.Node.Python.Value):
            return False

        if isinstance(node, SCons.Node.Alias.Alias):
            build = alias_to_ninja_build(node)
        else:
            build = self.translator.action_to_ninja_build(node)

        # Some things are unbuild-able or need not be built in Ninja
        if build is None:
            return False

        node_string = str(node)
        if node_string in self.builds:
            # TODO: If we work out a way to handle Alias() with same name as file this logic can be removed
            # This works around adding Alias with the same name as a Node.
            # It's not great way to workaround because it force renames the alias,
            # but the alternative is broken ninja support.
            warn_msg = f"Alias {node_string} name the same as File node, ninja does not support this. Renaming Alias {node_string} to {node_string}_alias."
            if isinstance(node, SCons.Node.Alias.Alias):
                for i, output in enumerate(build["outputs"]):
                    if output == node_string:
                        build["outputs"][i] += "_alias"
                node_string += "_alias"
                print(warn_msg)
            elif self.builds[node_string]["rule"] == "phony":
                for i, output in enumerate(self.builds[node_string]["outputs"]):
                    if output == node_string:
                        self.builds[node_string]["outputs"][i] += "_alias"
                tmp_build = self.builds[node_string].copy()
                del self.builds[node_string]
                node_string += "_alias"
                self.builds[node_string] = tmp_build
                print(warn_msg)
            else:
                raise InternalError("Node {} added to ninja build state more than once".format(node_string))
        self.builds[node_string] = build
        return True

    # TODO: rely on SCons to tell us what is generated source
    # or some form of user scanner maybe (Github Issue #3624)
    def is_generated_source(self, output):
        """Check if output ends with a known generated suffix."""
        _, suffix = splitext(output)
        return suffix in self.generated_suffixes

    def has_generated_sources(self, output):
        """
        Determine if output indicates this is a generated header file.
        """
        for generated in output:
            if self.is_generated_source(generated):
                return True
        return False

    # pylint: disable=too-many-branches,too-many-locals
    def generate(self):
        """
        Generate the build.ninja.

        This should only be called once for the lifetime of this object.
        """
        if self.__generated:
            return

        num_jobs = self.env.get('NINJA_MAX_JOBS', self.env.GetOption("num_jobs"))
        self.pools.update({
            "local_pool": num_jobs,
            "install_pool": num_jobs / 2,
        })

        deps_format = self.env.get("NINJA_DEPFILE_PARSE_FORMAT", 'msvc' if self.env['PLATFORM'] == 'win32' else 'gcc')
        for rule in ["CC", "CXX"]:
            if deps_format == "msvc":
                self.rules[rule]["deps"] = "msvc"
            elif deps_format == "gcc" or deps_format == "clang":
                self.rules[rule]["deps"] = "gcc"
                self.rules[rule]["depfile"] = "$out.d"
            else:
                raise Exception(f"Unknown 'NINJA_DEPFILE_PARSE_FORMAT'={self.env['NINJA_DEPFILE_PARSE_FORMAT']}, use 'mvsc', 'gcc', or 'clang'.")

        for key, rule in self.env.get(NINJA_RULES, {}).items():
            # make a non response file rule for users custom response file rules.
            if rule.get('rspfile') is not None:
                self.rules.update({key + '_RSP': rule})
                non_rsp_rule = rule.copy()
                del non_rsp_rule['rspfile']
                del non_rsp_rule['rspfile_content']
                self.rules.update({key: non_rsp_rule})
            else:
                self.rules.update({key: rule})
        
        self.pools.update(self.env.get(NINJA_POOLS, {}))

        content = io.StringIO()
        ninja = self.writer_class(content, width=100)

        ninja.comment("Generated by scons. DO NOT EDIT.")

        ninja.variable("builddir", get_path(self.env.Dir(self.env['NINJA_DIR']).path))

        for pool_name, size in sorted(self.pools.items()):
            ninja.pool(pool_name, min(self.env.get('NINJA_MAX_JOBS', size), size))

        for var, val in sorted(self.variables.items()):
            ninja.variable(var, val)

        for rule, kwargs in sorted(self.rules.items()):
            if self.env.get('NINJA_MAX_JOBS') is not None and 'pool' not in kwargs:
                kwargs['pool'] = 'local_pool'
            ninja.rule(rule, **kwargs)

        # If the user supplied an alias to determine generated sources, use that, otherwise
        # determine what the generated sources are dynamically.
        generated_sources_alias = self.env.get('NINJA_GENERATED_SOURCE_ALIAS_NAME')
        generated_sources_build = None

        if generated_sources_alias:
            generated_sources_build = self.builds.get(generated_sources_alias)
            if generated_sources_build is None or generated_sources_build["rule"] != 'phony':
                raise Exception(
                    "ERROR: 'NINJA_GENERATED_SOURCE_ALIAS_NAME' set, but no matching Alias object found."
                )

        if generated_sources_alias and generated_sources_build:
            generated_source_files = sorted(
                [] if not generated_sources_build else generated_sources_build['implicit']
            )
            
            def check_generated_source_deps(build):
                return (
                    build != generated_sources_build
                    and set(build["outputs"]).isdisjoint(generated_source_files)
                )
        else:
            generated_sources_build = None
            generated_source_files = sorted({
                output
                # First find builds which have header files in their outputs.
                for build in self.builds.values()
                if self.has_generated_sources(build["outputs"])
                for output in build["outputs"]
                # Collect only the header files from the builds with them
                # in their output. We do this because is_generated_source
                # returns True if it finds a header in any of the outputs,
                # here we need to filter so we only have the headers and
                # not the other outputs.
                if self.is_generated_source(output)
            })

            if generated_source_files:
                generated_sources_alias = "_ninja_generated_sources"
                ninja.build(
                    outputs=generated_sources_alias,
                    rule="phony",
                    implicit=generated_source_files
                )
                
                def check_generated_source_deps(build):
                    return (
                        not build["rule"] == "INSTALL"
                        and set(build["outputs"]).isdisjoint(generated_source_files)
                        and set(build.get("implicit", [])).isdisjoint(generated_source_files)
                    )

        template_builders = []
        scons_compiledb = False

        if SCons.Script._Get_Default_Targets == SCons.Script._Set_Default_Targets_Has_Not_Been_Called:
            all_targets = set()
        else:
            all_targets = None

        for build in [self.builds[key] for key in sorted(self.builds.keys())]:
            if "compile_commands.json" in build["outputs"]:
                scons_compiledb = True

            # this is for the no command line targets, no SCons default case. We want this default
            # to just be all real files in the build.
            if all_targets is not None and build['rule'] != 'phony':
                all_targets = all_targets | set(build["outputs"])

            if build["rule"] == "TEMPLATE":
                template_builders.append(build)
                continue

            if "implicit" in build:
                build["implicit"].sort()

            # Don't make generated sources depend on each other. We
            # have to check that none of the outputs are generated
            # sources and none of the direct implicit dependencies are
            # generated sources or else we will create a dependency
            # cycle.
            if (
                generated_source_files
                and check_generated_source_deps(build)
            ):
                # Make all non-generated source targets depend on
                # _generated_sources. We use order_only for generated
                # sources so that we don't rebuild the world if one
                # generated source was rebuilt. We just need to make
                # sure that all of these sources are generated before
                # other builds.
                order_only = build.get("order_only", [])
                order_only.append(generated_sources_alias)
                build["order_only"] = order_only
            if "order_only" in build:
                build["order_only"].sort()

            # When using a depfile Ninja can only have a single output
            # but SCons will usually have emitted an output for every
            # thing a command will create because it's caching is much
            # more complex than Ninja's. This includes things like DWO
            # files. Here we make sure that Ninja only ever sees one
            # target when using a depfile. It will still have a command
            # that will create all of the outputs but most targets don't
            # depend directly on DWO files and so this assumption is safe
            # to make.
            rule = self.rules.get(build["rule"])

            # Some rules like 'phony' and other builtins we don't have
            # listed in self.rules so verify that we got a result
            # before trying to check if it has a deps key.
            #
            # Anything using deps or rspfile in Ninja can only have a single
            # output, but we may have a build which actually produces
            # multiple outputs which other targets can depend on. Here we
            # slice up the outputs so we have a single output which we will
            # use for the "real" builder and multiple phony targets that
            # match the file names of the remaining outputs. This way any
            # build can depend on any output from any build.
            #
            # We assume that the first listed output is the 'key'
            # output and is stably presented to us by SCons. For
            # instance if -gsplit-dwarf is in play and we are
            # producing foo.o and foo.dwo, we expect that outputs[0]
            # from SCons will be the foo.o file and not the dwo
            # file. If instead we just sorted the whole outputs array,
            # we would find that the dwo file becomes the
            # first_output, and this breaks, for instance, header
            # dependency scanning.
            if rule is not None and (rule.get("deps") or rule.get("rspfile")):
                first_output, remaining_outputs = (
                    build["outputs"][0],
                    build["outputs"][1:],
                )

                if remaining_outputs:
                    ninja_sorted_build(
                        ninja,
                        outputs=remaining_outputs, rule="phony", implicit=first_output,
                    )

                build["outputs"] = first_output

            # Optionally a rule can specify a depfile, and SCons can generate implicit
            # dependencies into the depfile. This allows for dependencies to come and go
            # without invalidating the ninja file. The depfile was created in ninja specifically
            # for dealing with header files appearing and disappearing across rebuilds, but it can
            # be repurposed for anything, as long as you have a way to regenerate the depfile.
            # More specific info can be found here: https://ninja-build.org/manual.html#_depfile
            if rule is not None and rule.get('depfile') and build.get('deps_files'):
                path = build['outputs'] if SCons.Util.is_List(build['outputs']) else [build['outputs']]
                generate_depfile(self.env, path[0], build.pop('deps_files', []))

            if "inputs" in build:
                build["inputs"].sort()

            ninja_sorted_build(
                ninja,
                **build
            )

        scons_daemon_dirty = str(pathlib.Path(get_path(self.env.get("NINJA_DIR"))) / "scons_daemon_dirty")
        for template_builder in template_builders:
            template_builder["implicit"] += [scons_daemon_dirty]
            ninja_sorted_build(
                ninja,
                **template_builder
            )

        # We have to glob the SCons files here to teach the ninja file
        # how to regenerate itself. We'll never see ourselves in the
        # DAG walk so we can't rely on action_to_ninja_build to
        # generate this rule even though SCons should know we're
        # dependent on SCons files.
        ninja_file_path = self.env.File(self.ninja_file).path
        regenerate_deps = to_escaped_list(self.env, self.env['NINJA_REGENERATE_DEPS'])

        ninja_sorted_build(
            ninja,
            outputs=ninja_file_path,
            rule="REGENERATE",
            implicit=regenerate_deps,
            variables={
                "self": ninja_file_path
            }
        )

        ninja_sorted_build(
            ninja,
            outputs=regenerate_deps,
            rule="phony",
            variables={
                "self": ninja_file_path,
            }
        )

        if not scons_compiledb:
            # If we ever change the name/s of the rules that include
            # compile commands (i.e. something like CC) we will need to
            # update this build to reflect that complete list.
            ninja_sorted_build(
                ninja,
                outputs="compile_commands.json",
                rule="CMD",
                pool="console",
                implicit=[str(self.ninja_file)],
                variables={
                    "cmd": "{} -f {} -t compdb {}CC CXX > compile_commands.json".format(
                        # NINJA_COMPDB_EXPAND - should only be true for ninja
                        # This was added to ninja's compdb tool in version 1.9.0 (merged April 2018)
                        # https://github.com/ninja-build/ninja/pull/1223
                        # TODO: add check in generate to check version and enable this by default if it's available.
                        self.ninja_bin_path, str(self.ninja_file),
                        '-x ' if self.env.get('NINJA_COMPDB_EXPAND', True) else ''
                    )
                },
            )

            ninja_sorted_build(
                ninja,
                outputs="compiledb", rule="phony", implicit=["compile_commands.json"],
            )

        ninja_sorted_build(
            ninja,
            outputs=["run_ninja_scons_daemon_phony", scons_daemon_dirty],
            rule="SCONS_DAEMON",
        )

        ninja.build(
            "shutdown_ninja_scons_daemon_phony",
            rule="EXIT_SCONS_DAEMON",
        )


        if all_targets is None:
            # Look in SCons's list of DEFAULT_TARGETS, find the ones that
            # we generated a ninja build rule for.
            all_targets = [str(node) for node in NINJA_DEFAULT_TARGETS]
        else:
            all_targets = list(all_targets)
        
        if len(all_targets) == 0:
            all_targets = ["phony_default"]
            ninja_sorted_build(
                ninja,
                outputs=all_targets,
                rule="phony",
            )
        
        ninja.default([self.ninja_syntax.escape_path(path) for path in sorted(all_targets)])

        with NamedTemporaryFile(delete=False, mode='w') as temp_ninja_file:
            temp_ninja_file.write(content.getvalue())

        if self.env.GetOption('skip_ninja_regen') and os.path.exists(ninja_file_path) and filecmp.cmp(temp_ninja_file.name, ninja_file_path):
            os.unlink(temp_ninja_file.name)
        else:

            daemon_dir = pathlib.Path(tempfile.gettempdir()) / ('scons_daemon_' + str(hashlib.md5(str(get_path(self.env["NINJA_DIR"])).encode()).hexdigest()))
            pidfile = None
            if os.path.exists(scons_daemon_dirty):
                pidfile = scons_daemon_dirty
            elif os.path.exists(daemon_dir / 'pidfile'):
                pidfile = daemon_dir / 'pidfile'

            if pidfile:
                with open(pidfile) as f:
                    pid = int(f.readline())
                    try:
                        os.kill(pid, signal.SIGINT)
                    except OSError:
                        pass

                # wait for the server process to fully killed
                # TODO: update wait_for_process_to_die() to handle timeout and then catch exception
                #       here and do something smart.
                wait_for_process_to_die(pid)

            if os.path.exists(scons_daemon_dirty):
                os.unlink(scons_daemon_dirty)

            shutil.move(temp_ninja_file.name, ninja_file_path)

        self.__generated = True


class SConsToNinjaTranslator:
    """Translates SCons Actions into Ninja build objects."""

    def __init__(self, env):
        self.env = env
        self.func_handlers = {
            # Skip conftest builders
            "_createSource": ninja_noop,
            # SCons has a custom FunctionAction that just makes sure the
            # target isn't static. We let the commands that ninja runs do
            # this check for us.
            "SharedFlagChecker": ninja_noop,
            # The install builder is implemented as a function action.
            # TODO: use command action #3573
            "installFunc": _install_action_function,
            "MkdirFunc": _mkdir_action_function,
            "Mkdir": _mkdir_action_function,
            "LibSymlinksActionFunction": _lib_symlink_action_function,
            "Copy": _copy_action_function
        }

        self.loaded_custom = False

    # pylint: disable=too-many-return-statements
    def action_to_ninja_build(self, node, action=None):
        """Generate build arguments dictionary for node."""

        if not self.loaded_custom:
            self.func_handlers.update(self.env[NINJA_CUSTOM_HANDLERS])
            self.loaded_custom = True

        if node.builder is None:
            return None

        if action is None:
            action = node.builder.action

        if node.env and node.env.get("NINJA_SKIP"):
            return None

        build = {}
        env = node.env if node.env else self.env

        # Ideally this should never happen, and we do try to filter
        # Ninja builders out of being sources of ninja builders but I
        # can't fix every DAG problem so we just skip ninja_builders
        # if we find one
        if SCons.Tool.ninja.NINJA_STATE.ninja_file == str(node):
            build = None
        elif isinstance(action, SCons.Action.FunctionAction):
            build = self.handle_func_action(node, action)
        elif isinstance(action, SCons.Action.LazyAction):
            # pylint: disable=protected-access
            action = action._generate_cache(env)
            build = self.action_to_ninja_build(node, action=action)
        elif isinstance(action, SCons.Action.ListAction):
            build = self.handle_list_action(node, action)
        elif isinstance(action, COMMAND_TYPES):
            build = get_command(env, node, action)
        else:
            return {
                "rule": "TEMPLATE",
                "order_only": get_order_only(node),
                "outputs": get_outputs(node),
                "inputs": get_inputs(node),
                "implicit": get_dependencies(node, skip_sources=True),
            }

        if build is not None:
            build["order_only"] = get_order_only(node)

        # TODO: WPD Is this testing the filename to verify it's a configure context generated file?
        if not node.is_conftest():
            node_callback = node.check_attributes("ninja_build_callback")
            if callable(node_callback):
                node_callback(env, node, build)

        return build

    def handle_func_action(self, node, action):
        """Determine how to handle the function action."""
        name = action.function_name()
        # This is the name given by the Subst/Textfile builders. So return the
        # node to indicate that SCons is required. We skip sources here because
        # dependencies don't really matter when we're going to shove these to
        # the bottom of ninja's DAG anyway and Textfile builders can have text
        # content as their source which doesn't work as an implicit dep in
        # ninja.
        if name == 'ninja_builder':
            return None

        handler = self.func_handlers.get(name, None)
        if handler is not None:
            return handler(node.env if node.env else self.env, node)
        elif name == "ActionCaller":
            action_to_call = str(action).split('(')[0].strip()
            handler = self.func_handlers.get(action_to_call, None)
            if handler is not None:
                return handler(node.env if node.env else self.env, node)

        SCons.Warnings.SConsWarning(
            "Found unhandled function action {}, "
            " generating scons command to build\n"
            "Note: this is less efficient than Ninja,"
            " you can write your own ninja build generator for"
            " this function using NinjaRegisterFunctionHandler".format(name)
        )

        return {
            "rule": "TEMPLATE",
            "order_only": get_order_only(node),
            "outputs": get_outputs(node),
            "inputs": get_inputs(node),
            "implicit": get_dependencies(node, skip_sources=True),
        }

    # pylint: disable=too-many-branches
    def handle_list_action(self, node, action):
        """TODO write this comment"""
        results = [
            self.action_to_ninja_build(node, action=act)
            for act in action.list
            if act is not None
        ]
        results = [
            result for result in results if result is not None and result["outputs"]
        ]
        if not results:
            return None

        # No need to process the results if we only got a single result
        if len(results) == 1:
            return results[0]

        all_outputs = list({output for build in results for output in build["outputs"]})
        dependencies = list({dep for build in results for dep in build.get("implicit", [])})

        if results[0]["rule"] == "CMD" or results[0]["rule"] == "GENERATED_CMD":
            cmdline = ""
            for cmd in results:

                # Occasionally a command line will expand to a
                # whitespace only string (i.e. '  '). Which is not a
                # valid command but does not trigger the empty command
                # condition if not cmdstr. So here we strip preceding
                # and proceeding whitespace to make strings like the
                # above become empty strings and so will be skipped.
                if not cmd.get("variables") or not cmd["variables"].get("cmd"):
                    continue

                cmdstr = cmd["variables"]["cmd"].strip()
                if not cmdstr:
                    continue

                # Skip duplicate commands
                if cmdstr in cmdline:
                    continue

                if cmdline:
                    cmdline += " && "

                cmdline += cmdstr

            # Remove all preceding and proceeding whitespace
            cmdline = cmdline.strip()
            env = node.env if node.env else self.env
            executor = node.get_executor()
            if executor is not None:
                targets = executor.get_all_targets()
            else:
                if hasattr(node, "target_peers"):
                    targets = node.target_peers
                else:
                    targets = [node]

            # Make sure we didn't generate an empty cmdline
            if cmdline:
                ninja_build = {
                    "outputs": all_outputs,
                    "rule": get_rule(node, "GENERATED_CMD"),
                    "variables": {
                        "cmd": cmdline,
                        "env": get_command_env(env, targets, node.sources),
                    },
                    "implicit": dependencies,
                }

                if node.env and node.env.get("NINJA_POOL", None) is not None:
                    ninja_build["pool"] = node.env["pool"]

                return ninja_build

        elif results[0]["rule"] == "phony":
            return {
                "outputs": all_outputs,
                "rule": "phony",
                "implicit": dependencies,
            }

        elif results[0]["rule"] == "INSTALL":
            return {
                "outputs": all_outputs,
                "rule": get_rule(node, "INSTALL"),
                "inputs": get_inputs(node),
                "implicit": dependencies,
            }

        return {
            "rule": "TEMPLATE",
            "order_only": get_order_only(node),
            "outputs": get_outputs(node),
            "inputs": get_inputs(node),
            "implicit": get_dependencies(node, skip_sources=True),
        }
