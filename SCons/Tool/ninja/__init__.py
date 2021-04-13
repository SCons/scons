# MIT License
#
# Copyright 2020 MongoDB Inc.
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

"""Generate build.ninja files from SCons aliases."""

import importlib
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
from glob import glob

import SCons
import SCons.Tool.ninja.Globals
from SCons.Script import GetOption

from .Globals import NINJA_RULES, NINJA_POOLS, NINJA_CUSTOM_HANDLERS
from .NinjaState import NinjaState
from .Util import ninja_add_command_line_options, \
    get_path, ninja_noop, get_command, get_command_env, get_comstr, get_generic_shell_command, \
    generate_command

NINJA_STATE = None


def gen_get_response_file_command(env, rule, tool, tool_is_dynamic=False, custom_env={}):
    """Generate a response file command provider for rule name."""

    # If win32 using the environment with a response file command will cause
    # ninja to fail to create the response file. Additionally since these rules
    # generally are not piping through cmd.exe /c any environment variables will
    # make CreateProcess fail to start.
    #
    # On POSIX we can still set environment variables even for compile
    # commands so we do so.
    use_command_env = not env["PLATFORM"] == "win32"
    if "$" in tool:
        tool_is_dynamic = True

    def get_response_file_command(env, node, action, targets, sources, executor=None):
        if hasattr(action, "process"):
            cmd_list, _, _ = action.process(targets, sources, env, executor=executor)
            cmd_list = [str(c).replace("$", "$$") for c in cmd_list[0]]
        else:
            command = generate_command(
                env, node, action, targets, sources, executor=executor
            )
            cmd_list = shlex.split(command)

        if tool_is_dynamic:
            tool_command = env.subst(
                tool, target=targets, source=sources, executor=executor
            )
        else:
            tool_command = tool

        try:
            # Add 1 so we always keep the actual tool inside of cmd
            tool_idx = cmd_list.index(tool_command) + 1
        except ValueError:
            raise Exception(
                "Could not find tool {} in {} generated from {}".format(
                    tool, cmd_list, get_comstr(env, action, targets, sources)
                )
            )

        cmd, rsp_content = cmd_list[:tool_idx], cmd_list[tool_idx:]
        rsp_content = ['"' + rsp_content_item + '"' for rsp_content_item in rsp_content]
        rsp_content = " ".join(rsp_content)

        variables = {"rspc": rsp_content}
        variables[rule] = cmd
        if use_command_env:
            variables["env"] = get_command_env(env)

            for key, value in custom_env.items():
                variables["env"] += env.subst(
                    "export %s=%s;" % (key, value), target=targets, source=sources, executor=executor
                ) + " "
        return rule, variables, [tool_command]

    return get_response_file_command


def ninja_builder(env, target, source):
    """Generate a build.ninja for source."""
    if not isinstance(source, list):
        source = [source]
    if not isinstance(target, list):
        target = [target]

    # We have no COMSTR equivalent so print that we're generating
    # here.
    print("Generating:", str(target[0]))

    generated_build_ninja = target[0].get_abspath()
    NINJA_STATE.generate()

    if env["PLATFORM"] == "win32":
        # this is not great, its doesn't consider specific
        # node environments, which means on linux the build could
        # behave differently, because on linux you can set the environment
        # per command in the ninja file. This is only needed if
        # running ninja directly from a command line that hasn't
        # had the environment setup (vcvarsall.bat)
        with open('run_ninja_env.bat', 'w') as f:
            for key in env['ENV']:
                f.write('set {}={}\n'.format(key, env['ENV'][key]))
            f.write('{} -f {} %*\n'.format(NINJA_STATE.ninja_bin_path, generated_build_ninja))
        cmd = ['run_ninja_env.bat']

    else:
        cmd = [NINJA_STATE.ninja_bin_path, '-f', generated_build_ninja]

    if not env.get("DISABLE_AUTO_NINJA"):
        print("Executing:", str(' '.join(cmd)))

        # execute the ninja build at the end of SCons, trying to
        # reproduce the output like a ninja build would
        def execute_ninja():

            proc = subprocess.Popen(cmd,
                                    stderr=sys.stderr,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True,
                                    env=os.environ if env["PLATFORM"] == "win32" else env['ENV']
                                    )
            for stdout_line in iter(proc.stdout.readline, ""):
                yield stdout_line
            proc.stdout.close()
            return_code = proc.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, 'ninja')

        erase_previous = False
        for output in execute_ninja():
            output = output.strip()
            if erase_previous:
                sys.stdout.write('\x1b[2K')  # erase previous line
                sys.stdout.write("\r")
            else:
                sys.stdout.write(os.linesep)
            sys.stdout.write(output)
            sys.stdout.flush()
            # this will only erase ninjas [#/#] lines
            # leaving warnings and other output, seems a bit
            # prone to failure with such a simple check
            erase_previous = output.startswith('[')

# pylint: disable=too-few-public-methods
class AlwaysExecAction(SCons.Action.FunctionAction):
    """Override FunctionAction.__call__ to always execute."""

    def __call__(self, *args, **kwargs):
        kwargs["execute"] = 1
        return super().__call__(*args, **kwargs)


def register_custom_handler(env, name, handler):
    """Register a custom handler for SCons function actions."""
    env[NINJA_CUSTOM_HANDLERS][name] = handler


def register_custom_rule_mapping(env, pre_subst_string, rule):
    """Register a function to call for a given rule."""
    SCons.Tool.ninja.Globals.__NINJA_RULE_MAPPING[pre_subst_string] = rule


def register_custom_rule(env, rule, command, description="", deps=None, pool=None, use_depfile=False, use_response_file=False, response_file_content="$rspc"):
    """Allows specification of Ninja rules from inside SCons files."""
    rule_obj = {
        "command": command,
        "description": description if description else "{} $out".format(rule),
    }

    if use_depfile:
        rule_obj["depfile"] = os.path.join(get_path(env['NINJA_BUILDDIR']), '$out.depfile')

    if deps is not None:
        rule_obj["deps"] = deps

    if pool is not None:
        rule_obj["pool"] = pool

    if use_response_file:
        rule_obj["rspfile"] = "$out.rsp"
        rule_obj["rspfile_content"] = response_file_content

    env[NINJA_RULES][rule] = rule_obj


def register_custom_pool(env, pool, size):
    """Allows the creation of custom Ninja pools"""
    env[NINJA_POOLS][pool] = size


def set_build_node_callback(env, node, callback):
    if not node.is_conftest():
        node.attributes.ninja_build_callback = callback


def ninja_csig(original):
    """Return a dummy csig"""

    def wrapper(self):
        if isinstance(self, SCons.Node.Node) and self.is_sconscript():
            return original(self)
        return "dummy_ninja_csig"

    return wrapper


def ninja_contents(original):
    """Return a dummy content without doing IO"""

    def wrapper(self):
        if isinstance(self, SCons.Node.Node) and self.is_sconscript():
            return original(self)
        return bytes("dummy_ninja_contents", encoding="utf-8")

    return wrapper


def CheckNinjaCompdbExpand(env, context):
    """ Configure check testing if ninja's compdb can expand response files"""

    context.Message('Checking if ninja compdb can expand response files... ')
    ret, output = context.TryAction(
        action='ninja -f $SOURCE -t compdb -x CMD_RSP > $TARGET',
        extension='.ninja',
        text=textwrap.dedent("""
            rule CMD_RSP
              command = $cmd @$out.rsp > fake_output.txt
              description = Building $out
              rspfile = $out.rsp
              rspfile_content = $rspc
            build fake_output.txt: CMD_RSP fake_input.txt
              cmd = echo
              pool = console
              rspc = "test"
            """))
    result = '@fake_output.txt.rsp' not in output
    context.Result(result)
    return result


def ninja_stat(_self, path):
    """
    Eternally memoized stat call.

    SCons is very aggressive about clearing out cached values. For our
    purposes everything should only ever call stat once since we're
    running in a no_exec build the file system state should not
    change. For these reasons we patch SCons.Node.FS.LocalFS.stat to
    use our eternal memoized dictionary.
    """

    try:
        return SCons.Tool.ninja.Globals.NINJA_STAT_MEMO[path]
    except KeyError:
        try:
            result = os.stat(path)
        except os.error:
            result = None

        SCons.Tool.ninja.Globals.NINJA_STAT_MEMO[path] = result
        return result


def ninja_whereis(thing, *_args, **_kwargs):
    """Replace env.WhereIs with a much faster version"""

    # Optimize for success, this gets called significantly more often
    # when the value is already memoized than when it's not.
    try:
        return SCons.Tool.ninja.Globals.NINJA_WHEREIS_MEMO[thing]
    except KeyError:
        # We do not honor any env['ENV'] or env[*] variables in the
        # generated ninja file. Ninja passes your raw shell environment
        # down to it's subprocess so the only sane option is to do the
        # same during generation. At some point, if and when we try to
        # upstream this, I'm sure a sticking point will be respecting
        # env['ENV'] variables and such but it's actually quite
        # complicated. I have a naive version but making it always work
        # with shell quoting is nigh impossible. So I've decided to
        # cross that bridge when it's absolutely required.
        path = shutil.which(thing)
        SCons.Tool.ninja.Globals.NINJA_WHEREIS_MEMO[thing] = path
        return path


def ninja_always_serial(self, num, taskmaster):
    """Replacement for SCons.Job.Jobs constructor which always uses the Serial Job class."""
    # We still set self.num_jobs to num even though it's a lie. The
    # only consumer of this attribute is the Parallel Job class AND
    # the Main.py function which instantiates a Jobs class. It checks
    # if Jobs.num_jobs is equal to options.num_jobs, so if the user
    # provides -j12 but we set self.num_jobs = 1 they get an incorrect
    # warning about this version of Python not supporting parallel
    # builds. So here we lie so the Main.py will not give a false
    # warning to users.
    self.num_jobs = num
    self.job = SCons.Job.Serial(taskmaster)

def ninja_hack_linkcom(env):
    # TODO: change LINKCOM and SHLINKCOM to handle embedding manifest exe checks
    # without relying on the SCons hacks that SCons uses by default.
    if env["PLATFORM"] == "win32":
        from SCons.Tool.mslink import compositeLinkAction

        if env.get("LINKCOM", None) == compositeLinkAction:
            env[
                "LINKCOM"
            ] = '${TEMPFILE("$LINK $LINKFLAGS /OUT:$TARGET.windows $_LIBDIRFLAGS $_LIBFLAGS $_PDB $SOURCES.windows", "$LINKCOMSTR")}'
            env[
                "SHLINKCOM"
            ] = '${TEMPFILE("$SHLINK $SHLINKFLAGS $_SHLINK_TARGETS $_LIBDIRFLAGS $_LIBFLAGS $_PDB $_SHLINK_SOURCES", "$SHLINKCOMSTR")}'


def ninja_print_conf_log(s, target, source, env):
    """Command line print only for conftest to generate a correct conf log."""
    if target and target[0].is_conftest():
        action = SCons.Action._ActionAction()
        action.print_cmd_line(s, target, source, env)


class NinjaNoResponseFiles(SCons.Platform.TempFileMunge):
    """Overwrite the __call__ method of SCons' TempFileMunge to not delete."""

    def __call__(self, target, source, env, for_signature):
        return self.cmd

    def _print_cmd_str(*_args, **_kwargs):
        """Disable this method"""
        pass


def exists(env):
    """Enable if called."""

    if 'ninja' not in GetOption('experimental'):
        return False

    # This variable disables the tool when storing the SCons command in the
    # generated ninja file to ensure that the ninja tool is not loaded when
    # SCons should do actual work as a subprocess of a ninja build. The ninja
    # tool is very invasive into the internals of SCons and so should never be
    # enabled when SCons needs to build a target.
    if env.get("__NINJA_NO", "0") == "1":
        return False

    try:
        import ninja
        return ninja.__file__
    except ImportError:
        SCons.Warnings.SConsWarning("Failed to import ninja, attempt normal SCons build.")
        return False


def ninja_emitter(target, source, env):
    """ fix up the source/targets """

    ninja_file = env.File(env.subst("$NINJA_FILE_NAME"))
    ninja_file.attributes.ninja_file = True

    # Someone called env.Ninja('my_targetname.ninja')
    if not target and len(source) == 1:
        target = source

    # Default target name is $NINJA_PREFIX.$NINJA.SUFFIX
    if not target:
        target = [ninja_file, ]

    # No source should have been passed. Drop it.
    if source:
        source = []

    return target, source


def generate(env):
    """Generate the NINJA builders."""
    global NINJA_STATE

    if 'ninja' not in GetOption('experimental'):
        return

    if not SCons.Tool.ninja.Globals.ninja_builder_initialized:
        SCons.Tool.ninja.Globals.ninja_builder_initialized = True

        ninja_add_command_line_options()

    try:
        import ninja # noqa: F401
    except ImportError:
        SCons.Warnings.SConsWarning("Failed to import ninja, attempt normal SCons build.")
        return

    env["DISABLE_AUTO_NINJA"] = GetOption('disable_execute_ninja')

    env["NINJA_FILE_NAME"] = env.get("NINJA_FILE_NAME", "build.ninja")

    # Add the Ninja builder.
    always_exec_ninja_action = AlwaysExecAction(ninja_builder, {})
    ninja_builder_obj = SCons.Builder.Builder(action=always_exec_ninja_action,
                                              emitter=ninja_emitter)
    env.Append(BUILDERS={"Ninja": ninja_builder_obj})

    env["NINJA_ALIAS_NAME"] = env.get("NINJA_ALIAS_NAME", "generate-ninja")
    env['NINJA_BUILDDIR'] = env.get("NINJA_BUILDDIR", env.Dir(".ninja").path)

    # here we allow multiple environments to construct rules and builds
    # into the same ninja file
    if NINJA_STATE is None:
        ninja_file = env.Ninja()
        env.AlwaysBuild(ninja_file)
        env.Alias("$NINJA_ALIAS_NAME", ninja_file)
    else:
        if str(NINJA_STATE.ninja_file) != env["NINJA_FILE_NAME"]:
            SCons.Warnings.SConsWarning("Generating multiple ninja files not supported, set ninja file name before tool initialization.")
        ninja_file = [NINJA_STATE.ninja_file]

    # TODO: API for getting the SConscripts programmatically
    # exists upstream: https://github.com/SCons/scons/issues/3625
    def ninja_generate_deps(env):
        return sorted([env.File("#SConstruct").path] + glob("**/SConscript", recursive=True))
    env['_NINJA_REGENERATE_DEPS_FUNC'] = ninja_generate_deps

    env['NINJA_REGENERATE_DEPS'] = env.get('NINJA_REGENERATE_DEPS', '${_NINJA_REGENERATE_DEPS_FUNC(__env__)}')

    # This adds the required flags such that the generated compile
    # commands will create depfiles as appropriate in the Ninja file.
    if env["PLATFORM"] == "win32":
        env.Append(CCFLAGS=["/showIncludes"])
    else:
        env.Append(CCFLAGS=["-MMD", "-MF", "${TARGET}.d"])

    env.AddMethod(CheckNinjaCompdbExpand, "CheckNinjaCompdbExpand")

    # Provide a way for custom rule authors to easily access command
    # generation.
    env.AddMethod(get_generic_shell_command, "NinjaGetGenericShellCommand")
    env.AddMethod(get_command, "NinjaGetCommand")
    env.AddMethod(gen_get_response_file_command, "NinjaGenResponseFileProvider")
    env.AddMethod(set_build_node_callback, "NinjaSetBuildNodeCallback")

    # Provides a way for users to handle custom FunctionActions they
    # want to translate to Ninja.
    env[NINJA_CUSTOM_HANDLERS] = {}
    env.AddMethod(register_custom_handler, "NinjaRegisterFunctionHandler")

    # Provides a mechanism for inject custom Ninja rules which can
    # then be mapped using NinjaRuleMapping.
    env[NINJA_RULES] = {}
    env.AddMethod(register_custom_rule, "NinjaRule")

    # Provides a mechanism for inject custom Ninja pools which can
    # be used by providing the NINJA_POOL="name" as an
    # OverrideEnvironment variable in a builder call.
    env[NINJA_POOLS] = {}
    env.AddMethod(register_custom_pool, "NinjaPool")

    # Add the ability to register custom NinjaRuleMappings for Command
    # builders. We don't store this dictionary in the env to prevent
    # accidental deletion of the CC/XXCOM mappings. You can still
    # overwrite them if you really want to but you have to explicit
    # about it this way. The reason is that if they were accidentally
    # deleted you would get a very subtly incorrect Ninja file and
    # might not catch it.
    env.AddMethod(register_custom_rule_mapping, "NinjaRuleMapping")

    # on windows we need to change the link action
    ninja_hack_linkcom(env)

    # Normally in SCons actions for the Program and *Library builders
    # will return "${*COM}" as their pre-subst'd command line. However
    # if a user in a SConscript overwrites those values via key access
    # like env["LINKCOM"] = "$( $ICERUN $)" + env["LINKCOM"] then
    # those actions no longer return the "bracketted" string and
    # instead return something that looks more expanded. So to
    # continue working even if a user has done this we map both the
    # "bracketted" and semi-expanded versions.
    def robust_rule_mapping(var, rule, tool):
        provider = gen_get_response_file_command(env, rule, tool)
        env.NinjaRuleMapping("${" + var + "}", provider)
        env.NinjaRuleMapping(env.get(var, None), provider)

    robust_rule_mapping("CCCOM", "CC", "$CC")
    robust_rule_mapping("SHCCCOM", "CC", "$CC")
    robust_rule_mapping("CXXCOM", "CXX", "$CXX")
    robust_rule_mapping("SHCXXCOM", "CXX", "$CXX")
    robust_rule_mapping("LINKCOM", "LINK", "$LINK")
    robust_rule_mapping("SHLINKCOM", "LINK", "$SHLINK")
    robust_rule_mapping("ARCOM", "AR", "$AR")

    # Make SCons node walk faster by preventing unnecessary work
    env.Decider("timestamp-match")

    # Used to determine if a build generates a source file. Ninja
    # requires that all generated sources are added as order_only
    # dependencies to any builds that *might* use them.
    # TODO: switch to using SCons to help determine this (Github Issue #3624)
    env["NINJA_GENERATED_SOURCE_SUFFIXES"] = [".h", ".hpp"]

    if env["PLATFORM"] != "win32" and env.get("RANLIBCOM"):
        # There is no way to translate the ranlib list action into
        # Ninja so add the s flag and disable ranlib.
        #
        # This is equivalent to Meson.
        # https://github.com/mesonbuild/meson/blob/master/mesonbuild/linkers.py#L143
        old_arflags = str(env["ARFLAGS"])
        if "s" not in old_arflags:
            old_arflags += "s"

        env["ARFLAGS"] = SCons.Util.CLVar([old_arflags])

        # Disable running ranlib, since we added 's' above
        env["RANLIBCOM"] = ""

    if GetOption('disable_ninja'):
        return env

    SCons.Warnings.SConsWarning("Initializing ninja tool... this feature is experimental. SCons internals and all environments will be affected.")

    # This is the point of no return, anything after this comment
    # makes changes to SCons that are irreversible and incompatible
    # with a normal SCons build. We return early if __NINJA_NO=1 has
    # been given on the command line (i.e. by us in the generated
    # ninja file) here to prevent these modifications from happening
    # when we want SCons to do work. Everything before this was
    # necessary to setup the builder and other functions so that the
    # tool can be unconditionally used in the users's SCons files.

    if not exists(env):
        return

    # Set a known variable that other tools can query so they can
    # behave correctly during ninja generation.
    env["GENERATING_NINJA"] = True

    # These methods are no-op'd because they do not work during ninja
    # generation, expected to do no work, or simply fail. All of which
    # are slow in SCons. So we overwrite them with no logic.
    SCons.Node.FS.File.make_ready = ninja_noop
    SCons.Node.FS.File.prepare = ninja_noop
    SCons.Node.FS.File.push_to_cache = ninja_noop
    SCons.Executor.Executor.prepare = ninja_noop
    SCons.Taskmaster.Task.prepare = ninja_noop
    SCons.Node.FS.File.built = ninja_noop
    SCons.Node.Node.visited = ninja_noop

    # We make lstat a no-op because it is only used for SONAME
    # symlinks which we're not producing.
    SCons.Node.FS.LocalFS.lstat = ninja_noop

    # This is a slow method that isn't memoized. We make it a noop
    # since during our generation we will never use the results of
    # this or change the results.
    SCons.Node.FS.is_up_to_date = ninja_noop

    # We overwrite stat and WhereIs with eternally memoized
    # implementations. See the docstring of ninja_stat and
    # ninja_whereis for detailed explanations.
    SCons.Node.FS.LocalFS.stat = ninja_stat
    SCons.Util.WhereIs = ninja_whereis

    # Monkey patch get_csig and get_contents for some classes. It
    # slows down the build significantly and we don't need contents or
    # content signatures calculated when generating a ninja file since
    # we're not doing any SCons caching or building.
    SCons.Executor.Executor.get_contents = ninja_contents(
        SCons.Executor.Executor.get_contents
    )
    SCons.Node.Alias.Alias.get_contents = ninja_contents(
        SCons.Node.Alias.Alias.get_contents
    )
    SCons.Node.FS.File.get_contents = ninja_contents(SCons.Node.FS.File.get_contents)
    SCons.Node.FS.File.get_csig = ninja_csig(SCons.Node.FS.File.get_csig)
    SCons.Node.FS.Dir.get_csig = ninja_csig(SCons.Node.FS.Dir.get_csig)
    SCons.Node.Alias.Alias.get_csig = ninja_csig(SCons.Node.Alias.Alias.get_csig)

    # Ignore CHANGED_SOURCES and CHANGED_TARGETS. We don't want those
    # to have effect in a generation pass because the generator
    # shouldn't generate differently depending on the current local
    # state. Without this, when generating on Windows, if you already
    # had a foo.obj, you would omit foo.cpp from the response file. Do the same for UNCHANGED.
    SCons.Executor.Executor._get_changed_sources = SCons.Executor.Executor._get_sources
    SCons.Executor.Executor._get_changed_targets = SCons.Executor.Executor._get_targets
    SCons.Executor.Executor._get_unchanged_sources = SCons.Executor.Executor._get_sources
    SCons.Executor.Executor._get_unchanged_targets = SCons.Executor.Executor._get_targets

    # Replace false action messages with nothing.
    env["PRINT_CMD_LINE_FUNC"] = ninja_print_conf_log

    # This reduces unnecessary subst_list calls to add the compiler to
    # the implicit dependencies of targets. Since we encode full paths
    # in our generated commands we do not need these slow subst calls
    # as executing the command will fail if the file is not found
    # where we expect it.
    env["IMPLICIT_COMMAND_DEPENDENCIES"] = False

    # This makes SCons more aggressively cache MD5 signatures in the
    # SConsign file.
    # TODO: WPD shouldn't this be set to 0?
    env.SetOption("max_drift", 1)

    # The Serial job class is SIGNIFICANTLY (almost twice as) faster
    # than the Parallel job class for generating Ninja files. So we
    # monkey the Jobs constructor to only use the Serial Job class.
    SCons.Job.Jobs.__init__ = ninja_always_serial

    ninja_syntax = importlib.import_module(".ninja_syntax", package='ninja')

    if NINJA_STATE is None:
        NINJA_STATE = NinjaState(env, ninja_file[0], ninja_syntax.Writer)


    # TODO: this is hacking into scons, preferable if there were a less intrusive way
    # We will subvert the normal builder execute to make sure all the ninja file is dependent
    # on all targets generated from any builders
    SCons_Builder_BuilderBase__execute = SCons.Builder.BuilderBase._execute

    def NinjaBuilderExecute(self, env, target, source, overwarn={}, executor_kw={}):
        # this ensures all environments in which a builder executes from will
        # not create list actions for linking on windows
        ninja_hack_linkcom(env)
        targets = SCons_Builder_BuilderBase__execute(self, env, target, source, overwarn=overwarn, executor_kw=executor_kw)

        if not SCons.Util.is_List(target):
            target = [target]

        for target in targets:
            if target.check_attributes('ninja_file') is None and not target.is_conftest():
                env.Depends(ninja_file, targets)
        return targets
    SCons.Builder.BuilderBase._execute = NinjaBuilderExecute

    # Here we monkey patch the Task.execute method to not do a bunch of
    # unnecessary work. If a build is a regular builder (i.e not a conftest and
    # not our own Ninja builder) then we add it to the NINJA_STATE. Otherwise we
    # build it like normal. This skips all of the caching work that this method
    # would normally do since we aren't pulling any of these targets from the
    # cache.
    #
    # In the future we may be able to use this to actually cache the build.ninja
    # file once we have the upstream support for referencing SConscripts as File
    # nodes.
    def ninja_execute(self):

        target = self.targets[0]
        if target.check_attributes('ninja_file') is None or not target.is_conftest:
            NINJA_STATE.add_build(target)
        else:
            target.build()

    SCons.Taskmaster.Task.execute = ninja_execute

    # Make needs_execute always return true instead of determining out of
    # date-ness.
    SCons.Script.Main.BuildTask.needs_execute = lambda x: True

    # We will eventually need to overwrite TempFileMunge to make it
    # handle persistent tempfiles or get an upstreamed change to add
    # some configurability to it's behavior in regards to tempfiles.
    #
    # Set all three environment variables that Python's
    # tempfile.mkstemp looks at as it behaves differently on different
    # platforms and versions of Python.
    build_dir = env.subst("$BUILD_DIR")
    if build_dir == "":
        build_dir = "."
    os.environ["TMPDIR"] = env.Dir("{}/.response_files".format(build_dir)).get_abspath()
    os.environ["TEMP"] = os.environ["TMPDIR"]
    os.environ["TMP"] = os.environ["TMPDIR"]
    if not os.path.isdir(os.environ["TMPDIR"]):
        env.Execute(SCons.Defaults.Mkdir(os.environ["TMPDIR"]))

    env["TEMPFILE"] = NinjaNoResponseFiles
