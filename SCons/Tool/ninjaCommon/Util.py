import SCons
from SCons.Script import AddOption

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