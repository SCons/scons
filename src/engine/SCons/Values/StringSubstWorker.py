from typing import Callable

from SCons.Values.EnvironmentValue import EnvironmentValue, ValueTypes
from SCons.Values.ParsedEnvironmentValue import ParsedEnvironmentValue
from SCons.Values.EnvironmentValue import debug, SubstModes


class StringSubstWorker(object):
    """
    This is used to hold the work in progress for subst when processing a plain String.
    It should hold all the context needed to evaluate the requested evaluated string.
    """
    __slots__ = ['subst_val', 'return_value', 'string_values', 'parsed_values',
                 'new_string_values', 'new_parsed_values', 'mode', 'local_vars', 'global_vars', 'conv']

    def __init__(self, subst_val: EnvironmentValue, mode: SubstModes, local_vars, global_vars, conv: Callable):
        """
        :param subst_val: This should be EnvironmentValue.
        :param mode: Enum listing the type of substitution we're working on
        :param conv: Function to convert objects to return value
        """
        self.subst_val = subst_val
        self.mode = mode
        self.conv = conv
        self.local_vars = local_vars
        self.global_vars = global_vars

        # Array of lines made of an array of arguments.
        # Each argument can have N tokens.
        self.return_value = []

        value_length = len(subst_val.all_dependencies)

        # We initially separate parts of the subst_value into plain strings and parsed values
        # parsed values need to be further evaluated (think $VALUE, ${VALUE[1]}, ${VALUE.property}...
        self.string_values = [None] * value_length
        self.parsed_values = [None] * value_length

        # To hold values for work in progress. These can be updated with each pass while evaluating
        # remaining parsed_values.
        self.new_string_values = []
        self.new_parsed_values = []

    def add_token(self, token):
        self.return_value.append(token)

    def new_argument(self):
        pass
        # argument = "".join(self.current_value)
        # self.return_value[self.retval_index].append(argument)
        # self.current_value = []

    def new_line(self):
        pass
        # self.return_value.append[]
        # self.retval_index += 1

    def get_string(self) -> str:
        """

        :return: A string
        # TODO: Should this be a Literal or CmdStringHolder?
        # TODO: Should we return a tuple or object which contains a value for each subst type?
        """
        return "".join(self.return_value)

    def split_dependencies(self, reserved_name_set):
        """
        Split the dependencies for the value into strings and items which need further processing
        (parsed_values
        :param local_vars: A dictionary of variable values to override enclosing EnvironmentValues
        :return:
        """

        # Break parts in to simple strings or parts to be further evaluated
        for (t, v, i) in self.subst_val.all_dependencies:
            if t in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                self.string_values[i] = (v, t)
            elif t in (ValueTypes.VARIABLE, ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                self.parsed_values[i] = ParsedEnvironmentValue(t, v, i, self.local_vars)
            elif t == ValueTypes.CALLABLE:
                self.parsed_values[i] = ParsedEnvironmentValue(t, v, i, self.local_vars)
            elif t == ValueTypes.VARIABLE_OR_CALLABLE:
                self.parsed_values[i] = ParsedEnvironmentValue(t, v, i, self.local_vars)
            else:
                self.string_values[i] = (v, t)

        debug("Parsed values:%s  for %s [%s]" % (self.parsed_values, self.subst_val._parsed, self.string_values))

    def resolve_parsed_values(self, env):
        """
        :param env: EnvironmentValues object to use when resolving parsed values.
        :param target:
        :param source:
        :param global_vars:
        :param local_vars:
        :return:
        """
        # Ensure we don't go into an infinite loop of subst evaluations.
        iter_count = 0
        while any(self.parsed_values):
            # Now we can use the context (env, global_vars, local_vars) to decide
            # any uncertain types in parsed_values
            env.resolve_unassigned_types(self, self.global_vars, self.local_vars)

            # Now evaluate the parsed values. Note that some of these may expand into
            # multiple values and require expansion of parsed_values and string_values array
            (self.parsed_values, self.string_values) = env.evaluate_parsed_values(self,
                                                                                  self.global_vars, self.local_vars,
                                                                                  self.mode, self.conv)
            iter_count += 1
            if iter_count > 12:
                raise Exception("Too many iterations in subst() bailing out")
