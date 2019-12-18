from SCons.Subst import raise_exception
from SCons.Values.EnvironmentValue import ValueTypes
from SCons.Values import AllowableExceptions


class ParsedEnvironmentValue(object):
    """
    Hold information about values which are considered parsed (typically hold a variable and have a $ in them)
    """
    __slots__ = ['value', 'type', 'position', 'local_vars']

    def __init__(self, value_type, value, position, local_vars=None):
        """

        :param value_type:
        :param value:
        :param position:
        :param local_vars:
        """
        self.value = value
        self.type = value_type
        self.position = position
        self.local_vars = local_vars

    def __str__(self):
        return "Type:%s VAL:%s" % (self.type, self.value)

    def resolve_unassigned_types(self, env_vals, global_vars):
        """
        If the ParsedEnvironmentValue is not determined to be Callable or Variable yet, do so now.
        :param env_vals: The EnvironmentValues instance we're being called from
        :param global_vars: Global variables
        :return: 0 - No change, 1 - Changed, 2 - Move to string_values and clear
        """

        nt = self.type

        # Resolve whether callable or a variable
        if self.type == ValueTypes.VARIABLE_OR_CALLABLE:
            if self.value in self.local_vars:
                if callable(self.local_vars[self.value]):
                    nt = ValueTypes.CALLABLE
                else:
                    nt = ValueTypes.PARSED
            elif self.value in global_vars:
                if callable(global_vars[self.value]):
                    nt = ValueTypes.CALLABLE
                else:
                    nt = ValueTypes.PARSED
            else:
                nt = ValueTypes.PARSED

        # We should be able to resolve now if it's a variable or a callable.
        if self.type == ValueTypes.EVALUABLE:
            if '(' in self.value:
                nt = ValueTypes.EVALUABLE
            elif '.' not in self.value and '[' not in self.value:
                nt = ValueTypes.PARSED
                if self.value not in self.local_vars and self.value in env_vals:
                    # Something like ${VARIABLE}
                    nt = env_vals[self.value].var_type
                elif self.value in self.local_vars:
                    nt = ValueTypes.PARSED  # Should we have lvars type?
                else:
                    if NameError not in AllowableExceptions:
                        raise_exception(NameError(self.value), self.local_vars['TARGETS'], self.value)
                    else:
                        # Probably can skip this as we're going to wipe this ParsedEnvironmentValue from parsed_values
                        self.value = nt
                        return 2
            else:
                # Something else where eval'ing it should suffice to yield a good value.
                nt = ValueTypes.EVALUABLE

        if nt != self.type:
            # We've modified the type, so update parsed values
            self.type = nt
            return True
        else:
            return False
