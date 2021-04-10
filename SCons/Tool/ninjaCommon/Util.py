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
import os
from os.path import join as joinpath

import SCons
from SCons.Action import get_default_ENV, _string_from_cmd_list
from SCons.Script import AddOption
from SCons.Tool.ninjaCommon.Globals import __NINJA_RULE_MAPPING
from SCons.Util import is_List, flatten_sequence


def ninja_add_command_line_options():
    """
    Add additional command line arguments to SCons specific to the ninja tool
    """
    AddOption('--disable-execute-ninja',
              dest='disable_execute_ninja',
              metavar='BOOL',
              action="store_true",
              default=False,
              help='Disable ninja automatically building after scons')

    AddOption('--disable-ninja',
              dest='disable_ninja',
              metavar='BOOL',
              action="store_true",
              default=False,
              help='Disable ninja automatically building after scons')


def is_valid_dependent_node(node):
    """
    Return True if node is not an alias or is an alias that has children

    This prevents us from making phony targets that depend on other
    phony targets that will never have an associated ninja build
    target.

    We also have to specify that it's an alias when doing the builder
    check because some nodes (like src files) won't have builders but
    are valid implicit dependencies.
    """
    if isinstance(node, SCons.Node.Alias.Alias):
        return node.children()

    if not node.env:
        return True

    return not node.env.get("NINJA_SKIP")


def alias_to_ninja_build(node):
    """Convert an Alias node into a Ninja phony target"""
    return {
        "outputs": get_outputs(node),
        "rule": "phony",
        "implicit": [
            get_path(src_file(n)) for n in node.children() if is_valid_dependent_node(n)
        ],
    }


def check_invalid_ninja_node(node):
    return not isinstance(node, (SCons.Node.FS.Base, SCons.Node.Alias.Alias))


def filter_ninja_nodes(node_list):
    ninja_nodes = []
    for node in node_list:
        if isinstance(node, (SCons.Node.FS.Base, SCons.Node.Alias.Alias)):
            ninja_nodes.append(node)
        else:
            continue
    return ninja_nodes


def get_input_nodes(node):
    if node.get_executor() is not None:
        inputs = node.get_executor().get_all_sources()
    else:
        inputs = node.sources
    return inputs


def invalid_ninja_nodes(node, targets):
    result = False
    for node_list in [node.prerequisites, get_input_nodes(node), node.children(), targets]:
        if node_list:
            result = result or any([check_invalid_ninja_node(node) for node in node_list])
    return result


def get_order_only(node):
    """Return a list of order only dependencies for node."""
    if node.prerequisites is None:
        return []
    return [get_path(src_file(prereq)) for prereq in filter_ninja_nodes(node.prerequisites)]


def get_dependencies(node, skip_sources=False):
    """Return a list of dependencies for node."""
    if skip_sources:
        return [
            get_path(src_file(child))
            for child in filter_ninja_nodes(node.children())
            if child not in node.sources
        ]
    return [get_path(src_file(child)) for child in filter_ninja_nodes(node.children())]


def get_inputs(node):
    """Collect the Ninja inputs for node."""
    return [get_path(src_file(o)) for o in filter_ninja_nodes(get_input_nodes(node))]


def get_outputs(node):
    """Collect the Ninja outputs for node."""
    executor = node.get_executor()
    if executor is not None:
        outputs = executor.get_all_targets()
    else:
        if hasattr(node, "target_peers"):
            outputs = node.target_peers
        else:
            outputs = [node]

    outputs = [get_path(o) for o in filter_ninja_nodes(outputs)]

    return outputs


def get_targets_sources(node):
    executor = node.get_executor()
    if executor is not None:
        tlist = executor.get_all_targets()
        slist = executor.get_all_sources()
    else:
        if hasattr(node, "target_peers"):
            tlist = node.target_peers
        else:
            tlist = [node]
        slist = node.sources

    # Retrieve the repository file for all sources
    slist = [rfile(s) for s in slist]
    return tlist, slist

def get_path(node):
    """
    Return a fake path if necessary.

    As an example Aliases use this as their target name in Ninja.
    """
    if hasattr(node, "get_path"):
        return node.get_path()
    return str(node)


def rfile(node):
    """
    Return the repository file for node if it has one. Otherwise return node
    """
    if hasattr(node, "rfile"):
        return node.rfile()
    return node


def src_file(node):
    """Returns the src code file if it exists."""
    if hasattr(node, "srcnode"):
        src = node.srcnode()
        if src.stat() is not None:
            return src
    return get_path(node)

def get_rule(node, rule):
    tlist, slist = get_targets_sources(node)
    if invalid_ninja_nodes(node, tlist):
        return "TEMPLATE"
    else:
        return rule


def generate_depfile(env, node, dependencies):
    """
    Ninja tool function for writing a depfile. The depfile should include
    the node path followed by all the dependent files in a makefile format.

    dependencies arg can be a list or a subst generator which returns a list.
    """

    depfile = os.path.join(get_path(env['NINJA_BUILDDIR']), str(node) + '.depfile')

    # subst_list will take in either a raw list or a subst callable which generates
    # a list, and return a list of CmdStringHolders which can be converted into raw strings.
    # If a raw list was passed in, then scons_list will make a list of lists from the original
    # values and even subst items in the list if they are substitutable. Flatten will flatten
    # the list in that case, to ensure for either input we have a list of CmdStringHolders.
    deps_list = env.Flatten(env.subst_list(dependencies))

    # Now that we have the deps in a list as CmdStringHolders, we can convert them into raw strings
    # and make sure to escape the strings to handle spaces in paths. We also will sort the result
    # keep the order of the list consistent.
    escaped_depends = sorted([dep.escape(env.get("ESCAPE", lambda x: x)) for dep in deps_list])
    depfile_contents = str(node) + ": " + ' '.join(escaped_depends)

    need_rewrite = False
    try:
        with open(depfile, 'r') as f:
            need_rewrite = (f.read() != depfile_contents)
    except FileNotFoundError:
        need_rewrite = True

    if need_rewrite:
        os.makedirs(os.path.dirname(depfile) or '.', exist_ok=True)
        with open(depfile, 'w') as f:
            f.write(depfile_contents)


def ninja_noop(*_args, **_kwargs):
    """
    A general purpose no-op function.

    There are many things that happen in SCons that we don't need and
    also don't return anything. We use this to disable those functions
    instead of creating multiple definitions of the same thing.
    """
    return None


def get_command(env, node, action):  # pylint: disable=too-many-branches
    """Get the command to execute for node."""
    if node.env:
        sub_env = node.env
    else:
        sub_env = env
    executor = node.get_executor()
    tlist, slist = get_targets_sources(node)

    # Generate a real CommandAction
    if isinstance(action, SCons.Action.CommandGeneratorAction):
        # pylint: disable=protected-access
        action = action._generate(tlist, slist, sub_env, 1, executor=executor)

    variables = {}

    comstr = get_comstr(sub_env, action, tlist, slist)
    if not comstr:
        return None

    provider = __NINJA_RULE_MAPPING.get(comstr, get_generic_shell_command)
    rule, variables, provider_deps = provider(sub_env, node, action, tlist, slist, executor=executor)

    # Get the dependencies for all targets
    implicit = list({dep for tgt in tlist for dep in get_dependencies(tgt)})

    # Now add in the other dependencies related to the command,
    # e.g. the compiler binary. The ninja rule can be user provided so
    # we must do some validation to resolve the dependency path for ninja.
    for provider_dep in provider_deps:

        provider_dep = sub_env.subst(provider_dep)
        if not provider_dep:
            continue

        # If the tool is a node, then SCons will resolve the path later, if its not
        # a node then we assume it generated from build and make sure it is existing.
        if isinstance(provider_dep, SCons.Node.Node) or os.path.exists(provider_dep):
            implicit.append(provider_dep)
            continue

        # in some case the tool could be in the local directory and be suppled without the ext
        # such as in windows, so append the executable suffix and check.
        prog_suffix = sub_env.get('PROGSUFFIX', '')
        provider_dep_ext = provider_dep if provider_dep.endswith(prog_suffix) else provider_dep + prog_suffix
        if os.path.exists(provider_dep_ext):
            implicit.append(provider_dep_ext)
            continue

        # Many commands will assume the binary is in the path, so
        # we accept this as a possible input from a given command.

        provider_dep_abspath = sub_env.WhereIs(provider_dep) or sub_env.WhereIs(provider_dep, path=os.environ["PATH"])
        if provider_dep_abspath:
            implicit.append(provider_dep_abspath)
            continue

        # Possibly these could be ignore and the build would still work, however it may not always
        # rebuild correctly, so we hard stop, and force the user to fix the issue with the provided
        # ninja rule.
        raise Exception("Could not resolve path for %s dependency on node '%s'" % (provider_dep, node))

    ninja_build = {
        "order_only": get_order_only(node),
        "outputs": get_outputs(node),
        "inputs": get_inputs(node),
        "implicit": implicit,
        "rule": get_rule(node, rule),
        "variables": variables,
    }

    # Don't use sub_env here because we require that NINJA_POOL be set
    # on a per-builder call basis to prevent accidental strange
    # behavior like env['NINJA_POOL'] = 'console' and sub_env can be
    # the global Environment object if node.env is None.
    # Example:
    #
    # Allowed:
    #
    #     env.Command("ls", NINJA_POOL="ls_pool")
    #
    # Not allowed and ignored:
    #
    #     env["NINJA_POOL"] = "ls_pool"
    #     env.Command("ls")
    #
    # TODO: Why not alloe env['NINJA_POOL'] ? (bdbaddog)
    if node.env and node.env.get("NINJA_POOL", None) is not None:
        ninja_build["pool"] = node.env["NINJA_POOL"]

    return ninja_build


def get_command_env(env):
    """
    Return a string that sets the environment for any environment variables that
    differ between the OS environment and the SCons command ENV.

    It will be compatible with the default shell of the operating system.
    """
    try:
        return env["NINJA_ENV_VAR_CACHE"]
    except KeyError:
        pass

    # Scan the ENV looking for any keys which do not exist in
    # os.environ or differ from it. We assume if it's a new or
    # differing key from the process environment then it's
    # important to pass down to commands in the Ninja file.
    ENV = get_default_ENV(env)
    scons_specified_env = {
        key: value
        for key, value in ENV.items()
        # TODO: Remove this filter, unless there's a good reason to keep. SCons's behavior shouldn't depend on shell's.
        if key not in os.environ or os.environ.get(key, None) != value
    }

    windows = env["PLATFORM"] == "win32"
    command_env = ""
    for key, value in scons_specified_env.items():
        # Ensure that the ENV values are all strings:
        if is_List(value):
            # If the value is a list, then we assume it is a
            # path list, because that's a pretty common list-like
            # value to stick in an environment variable:
            value = flatten_sequence(value)
            value = joinpath(map(str, value))
        else:
            # If it isn't a string or a list, then we just coerce
            # it to a string, which is the proper way to handle
            # Dir and File instances and will produce something
            # reasonable for just about everything else:
            value = str(value)

        if windows:
            command_env += "set '{}={}' && ".format(key, value)
        else:
            # We address here *only* the specific case that a user might have
            # an environment variable which somehow gets included and has
            # spaces in the value. These are escapes that Ninja handles. This
            # doesn't make builds on paths with spaces (Ninja and SCons issues)
            # nor expanding response file paths with spaces (Ninja issue) work.
            value = value.replace(r' ', r'$ ')
            command_env += "export {}='{}';".format(key, value)

    env["NINJA_ENV_VAR_CACHE"] = command_env
    return command_env


def get_comstr(env, action, targets, sources):
    """Get the un-substituted string for action."""
    # Despite being having "list" in it's name this member is not
    # actually a list. It's the pre-subst'd string of the command. We
    # use it to determine if the command we're about to generate needs
    # to use a custom Ninja rule. By default this redirects CC, CXX,
    # AR, SHLINK, and LINK commands to their respective rules but the
    # user can inject custom Ninja rules and tie them to commands by
    # using their pre-subst'd string.
    if hasattr(action, "process"):
        return action.cmd_list

    return action.genstring(targets, sources, env)


def get_generic_shell_command(env, node, action, targets, sources, executor=None):
    return (
        "CMD",
        {
            # TODO: Why is executor passed in and then ignored below? (bdbaddog)
            "cmd": generate_command(env, node, action, targets, sources, executor=None),
            "env": get_command_env(env),
        },
        # Since this function is a rule mapping provider, it must return a list of dependencies,
        # and usually this would be the path to a tool, such as a compiler, used for this rule.
        # However this function is to generic to be able to reliably extract such deps
        # from the command, so we return a placeholder empty list. It should be noted that
        # generally this function will not be used solely and is more like a template to generate
        # the basics for a custom provider which may have more specific options for a provider
        # function for a custom NinjaRuleMapping.
        []
    )


def generate_command(env, node, action, targets, sources, executor=None):
    # Actions like CommandAction have a method called process that is
    # used by SCons to generate the cmd_line they need to run. So
    # check if it's a thing like CommandAction and call it if we can.
    if hasattr(action, "process"):
        cmd_list, _, _ = action.process(targets, sources, env, executor=executor)
        cmd = _string_from_cmd_list(cmd_list[0])
    else:
        # Anything else works with genstring, this is most commonly hit by
        # ListActions which essentially call process on all of their
        # commands and concatenate it for us.
        genstring = action.genstring(targets, sources, env)
        if executor is not None:
            cmd = env.subst(genstring, executor=executor)
        else:
            cmd = env.subst(genstring, targets, sources)

        cmd = cmd.replace("\n", " && ").strip()
        if cmd.endswith("&&"):
            cmd = cmd[0:-2].strip()

    # Escape dollars as necessary
    return cmd.replace("$", "$$")