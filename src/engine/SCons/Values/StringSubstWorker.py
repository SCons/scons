import SCons.Values.EnvironmentValue as EnvironmentValue


class StringWorker(object):
    """
    This is used to hold the work in progress for subst when processing a plain String.
    """
    __slots__ = ['subst_val', 'return_value', 'string_values', 'parsed_values',
                 'new_string_values', 'new_parsed_values']

    def __init__(self, subst_val: EnvironmentValue):
        """
        :param subst_val: This should be EnvironmentValue.
        """
        self.subst_val = subst_val

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