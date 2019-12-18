import SCons.Warnings
from SCons.Util import semi_deepcopy

AllowableExceptions = (KeyError,)


# These names are (or will be) controlled by SCons; users should never
# set or override them.  This warning can optionally be turned off,
# but SCons will still ignore the illegal variable names even if it's off.
reserved_construction_var_names = [
    'CHANGED_SOURCES',
    'CHANGED_TARGETS',
    'SOURCE',
    'SOURCES',
    'TARGET',
    'TARGETS',
    'UNCHANGED_SOURCES',
    'UNCHANGED_TARGETS',
]
reserved_construction_var_names_set = set(reserved_construction_var_names)
future_reserved_construction_var_names = [
    # 'HOST_OS',
    # 'HOST_ARCH',
    # 'HOST_CPU',
]


def copy_non_reserved_keywords(dict):
    result = semi_deepcopy(dict)
    for k in list(result.keys()):
        if k in reserved_construction_var_names:
            msg = "Ignoring attempt to set reserved variable `$%s'"
            SCons.Warnings.warn(SCons.Warnings.ReservedVariableWarning, msg % k)
            del result[k]
    return result


def _set_reserved(env, key, value):
    msg = "Ignoring attempt to set reserved variable `$%s'"
    SCons.Warnings.warn(SCons.Warnings.ReservedVariableWarning, msg % key)


def _set_future_reserved(env, key, value):
    env._dict[key] = value
    msg = "`$%s' will be reserved in a future release and setting it will become ignored"
    SCons.Warnings.warn(SCons.Warnings.FutureReservedVariableWarning, msg % key)