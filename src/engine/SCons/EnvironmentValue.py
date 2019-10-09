import re

from collections import UserDict, UserList
from numbers import Number

from SCons.Util import is_String, is_Sequence, CLVar, flatten
from SCons.Subst import AllowableExceptions, raise_exception

# remove for non py3
from enum import Enum

_debug = False
if _debug:
    def debug(fmt, *args):
        # format when needed
        print(fmt % args)
else:
    # avoid any formatting overhead
    def debug(*unused):
        pass

# Regular expressions for splitting strings and handling substitutions,
# for use by the scons_subst() and scons_subst_list() functions:
#
# The first expression compiled matches all of the $-introduced tokens
# that we need to process in some way, and is used for substitutions.
# The expressions it matches are:
#
#       "$$"
#       "$("
#       "$)"
#       "$variable"             [must begin with alphabetic or underscore]
#       "${any stuff}"
#
# The second expression compiled is used for splitting strings into tokens
# to be processed, and it matches all of the tokens listed above, plus
# the following that affect how arguments do or don't get joined together:
#
#       "   "                   [white space]
#       "non-white-space"       [without any dollar signs]
#       "$"                     [single dollar sign]
#
dollar_exps_str = r'\$[\$\(\)]|\$[_a-zA-Z][\.\w]*|\${[^}]*}'
dollar_exps = re.compile(r'(%s)' % dollar_exps_str)
separate_args = re.compile(r'(%s|\s+|[^\s\$]+|\$)' % dollar_exps_str)



class SubstModes(object):
    """
    Enum to store subst mode values.
    From Manpage:
    The optional raw argument may be set to:
    0 (Default) By default, leading or trailing white space will be removed
      from the result. and all sequences of white space will be compressed
      to a single space character. Additionally, any $( and $) character
      sequences will be stripped from the returned string
    1 if you want to preserve white space and $(-$) sequences.
    2 if you want to strip all characters between any $( and $) pairs
      (as is done for signature calculation).
    """
    NORMAL = 0
    RAW = 1
    FOR_SIGNATURE = 2
    SUBST_LIST = 3


class ValueTypes(Enum):
    """
    Enum to store what type of value the variable holds.
    """
    UNKNOWN = 0
    STRING = 1
    CALLABLE = 2
    VARIABLE = 3
    PARSED = 4
    COLLECTION = 5
    WHITESPACE = 6
    FUNCTION_CALL = 7
    ESCAPE_START = 8  # $(
    ESCAPE_END = 9    # $)
    VARIABLE_OR_CALLABLE = 10
    SHELL_REDIRECT = 11  # see SHELL_REDIRECT_CHARACTERS below
    NUMBER = 12
    LITERAL = 13  # This is a string which should be expanded no further.
    NONE = 14
    EVALUABLE = 15
    RESERVED = 16

    strings = ['UNKNOWN',
               'STRING',
               'CALLABLE',
               'VARIABLE',
               'PARSED',
               'COLLECTION',
               'WHITESPACE',
               'FUNCTION_CALL',
               'ESCAPE_START',
               'ESCAPE_END',
               'VARIABLE_OR_CALLABLE',
               'SHELL_REDIRECT',
               'NUMBER',
               'LITERAL',
               'NONE',
               'EVALUABLE',
               'RESERVED'
               ]

    SHELL_REDIRECT_CHARACTERS = '<>|'

    @staticmethod
    def enum_name(value):
        try:
            return ValueTypes.strings[value]
        except TypeError:
            pass


class EnvironmentValueParseError(Exception):
    """
    TODO: Should this be some kind of SCons exception
    """
    pass


class EnvironmentValue(object):
    """
    Hold a single value. We're going to cache parsed version of the file
    We're going to keep track of variables which feed into this values evaluation
    """

    __slots__ = ['_parsed', 'all_dependencies', 'value', 'var_type', 'depends_on', 'value', 'cached']
    all_values = {}

    @classmethod
    def factory(cls, value):
        """
        Create new EnvironmentValue or return existing cached one
        NOTE: Have to handle the value being changed.. as objects may be shared by other contexts (Copy on write..)
        :param value:
        :return: EnvironmentValue object
        """
        try:
            return EnvironmentValue.all_values[value]
        except KeyError:
            no = EnvironmentValue(value)
            EnvironmentValue.all_values[value] = no
            return no

    def __init__(self, value):
        # TODO: Should cache initialization by keeping hash all previous values, since we don't evaluate
        #  in context in the Value itself.

        self.value = value
        self.var_type = ValueTypes.UNKNOWN
        self._parsed = []
        self.depends_on = set()
        self.all_dependencies = []
        self.set_value(value)

    def set_value(self, value):
        """
        Set the value and parse the value if that is reasonable
        :param name: The variables name
        :param value: The value
        :return: None
        """

        if callable(self.value):
            # TODO: Document adding dependencies to callables
            try:
                self.depends_on = set(self.value.env_dependencies)
            except AttributeError as e:
                # the callable doesn't have env dependencies set
                pass
            self.var_type = ValueTypes.CALLABLE
        else:
            self.parse_value()

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __contains__(self, item):
        return item in self.value

    def parse_value(self):
        """
        Scan the string and break into component values

        Sets the following properties
        self.var_type
        self._parsed
        self.cached
        """
        try:
            if is_String(self.value):
                self.var_type = ValueTypes.STRING

                if '$' in self.value:
                    # Now we need to parse the specified string
                    result = separate_args.findall(self.value)
                    self._parsed = result
                    self.var_type = ValueTypes.PARSED

                    # Now further process parsed string to find it's components
                    self.find_dependencies()
                elif self.value == ' ':
                    pass
                else:
                    self.cached = (self.value, self.value)
            elif self.value is None:
                self.var_type = ValueTypes.NONE
                self.cached = ('', '')
            elif isinstance(self.value, CLVar):
                # TODO: Handle CLVar's being set and invalidating cache...
                self.var_type = ValueTypes.STRING
                self._parsed = self.value
                has_variables = [s for s in self.value if '$' in s]
                if has_variables:
                    self.var_type = ValueTypes.PARSED
                else:
                    self.cached = (str(self.value), str(self.value))

            elif isinstance(self.value, (list, dict, tuple, UserDict, UserList)):
                # Not string and not a callable, Should be some value
                # like dict, tuple, list
                self.var_type = ValueTypes.COLLECTION

                # This fails if value is list of list  [['a','b','c']]
                # if len(self.value) == 1 and isinstance(self.value, (list, UserDict, tuple))\
                #         and '$' not in self.value[0]:
                #     # Short cut if we only have 1 value and it has no $'s
                #     self.cached = (str(self.value[0]), str(self.value[0]))

                self._parsed = flatten(self.value)
                self.find_dependencies()
                #TODO Handle lists
                #TODO Handle Dicts
            elif isinstance(self.value, Number):
                self.var_type = ValueTypes.NUMBER
            else:
                # check if a Literal
                try:
                    if self.value.is_literal():
                        self.var_type = ValueTypes.LITERAL
                        self.cached = (str(self.value), str(self.value))
                except AttributeError as e:
                    # Not a literal?
                    print("NOT LITERAL WHAT IS IT Value:%s" % self.value)

            pass
        except TypeError:
            # likely callable? either way we don't parse
            print("Value:%s"%self.value)

    def _parse_function_call_dependencies(self, item):
        """
        Parse a function all for all it's parameters.

        _stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)

        Should yield

        LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__
        Plus the function itself

        _stripixes

        Adds list of parameters to the set of variables this object depends on
        :param item: subst string which is function call to be parsed
        :return: set of dependencies
        """
        function_name, remainder = item.split('(')

        if remainder[-1] != ')':
            # This shouldn't happen raise Exception
            raise EnvironmentValueParseError("No closing paren parsing Environment value function call "+item)
        else:
            # drop commas and spaces
            # TODO: (Should we parse vs split and drop all white space?)
            parameters = remainder[:-1].split(', ')

        # Now add all parameters to list of variables the string generated from this EnvironmentValue
        # depends upon
        self.depends_on.add(function_name)
        for p in parameters:
            # TODO: Should we strip attribute and array selectors from parameters?
            # TARGET[0] -> TARGET,  TARGET.abspath -> TARGET

            if '.' in p:
                p = p.split('.', 1)[0]
            if '[' in p:
                p = p.split('[', 1)[0]

            self.depends_on.add(p)

        return parameters

    def find_dependencies(self):
        """
        Find all the values which this value depends on (one layer deep)
        :return:
        """
        all_dependencies = []
        for index, v in enumerate(self._parsed):
            # debug("Processing [%s]"%v)

            if len(v) == 1:
                all_dependencies.append((ValueTypes.STRING, v, index))
                continue

            s0, s1 = v[:2]
            if s0 != '$':
                # Not a variable so we don't care
                all_dependencies.append((ValueTypes.STRING, v, index))
                continue
            if s0 == '$' and s1 == '(':
                # Escaping of value from signature calculations
                all_dependencies.append((ValueTypes.ESCAPE_START, v, index))
                continue
            if s0 == '$' and s1 == ')':
                # Escaping of value from signature calculations
                all_dependencies.append((ValueTypes.ESCAPE_END, v, index))
                continue

            if s1 == '$':
                # A literal dollar sign so we don't care
                all_dependencies.append((ValueTypes.STRING, s1, index))
                continue
            if s1 == '{':
                # This is a function call and/or requires python evaluation
                # Can be x.property or x(VAR1,VAR2)
                # If we can detect all info which affects this then we can cache
                value = v[2:-1]

                if '(' in value:
                    # Parse call to see if we can determine other dependencies from parameters
                    self._parse_function_call_dependencies(value)
                    all_dependencies.append((ValueTypes.FUNCTION_CALL, value, index))
                elif '.' in value or '[' in value:
                    all_dependencies.append((ValueTypes.EVALUABLE, value, index))
                else:
                    # We will get here if we have ${AAA} and AAA equates to a non-callable (string)
                    all_dependencies.append((ValueTypes.VARIABLE_OR_CALLABLE, v[2:-1], index))
            elif '.' in v:
                all_dependencies.append((ValueTypes.EVALUABLE, v[1:], index))
            else:
                # Plain Variable or callable. So label VARIABLE_OR_CALLABLE
                all_dependencies.append((ValueTypes.VARIABLE_OR_CALLABLE,v[1:], index))

        self.all_dependencies = all_dependencies

        self.debug_print_parsed_parts(all_dependencies)

        depend_list = [v for (t, v, i) in all_dependencies
                       if t in (ValueTypes.VARIABLE_OR_CALLABLE, ValueTypes.VARIABLE, ValueTypes.CALLABLE)]

        self.depends_on = self.depends_on.union(set(depend_list))
        

    @staticmethod
    def debug_print_parsed_parts(all_dependencies):
        for (index, val) in enumerate(all_dependencies):
            if val:
                try:
                    (t, v, i) = val
                except TypeError:
                    t = val.type
                    v = val.value
                    i = val.position

                debug("[%4d] %20s, %5s, %s",index, ValueTypes.enum_name(t), i, v)
            else:
                debug("[%4d] %20s, %5s, %s",index,"None","None","None")

    def update(self, key, all_values):
        """
        A key in the parent environment has changed/been set, update this value
        :param key:
        :param all_values:
        :return:
        """

        # remove the cache because it's been invalidated
        try:
            del self.cached
        except AttributeError as e:
            # there was no cached... ignore
            pass

        # update self.all_dependencies to see if the type has changed.
        for (t,v,i) in self.all_dependencies:
            if v == key:
                debug("Matching key:%s -> (%s/%s/%s)",key,ValueTypes.enum_name(t),v,i)

                if callable(all_values[key].value):
                    t = ValueTypes.CALLABLE
                else:
                    t = ValueTypes.VARIABLE_OR_CALLABLE

                debug("Now         :%s -> (%s/%s/%s)",key,ValueTypes.enum_name(t),v,i)

                # This needs to trigger update of this variable as well..
                self.all_dependencies[i] = (t, v, i)

    @staticmethod
    def create_local_var_dict(target, source):
        """Create a dictionary for substitution of special
        construction variables.

        This translates the following special arguments:

        target - the target (object or array of objects),
                 used to generate the TARGET and TARGETS
                 construction variables

        source - the source (object or array of objects),
                 used to generate the SOURCES and SOURCE
                 construction variables
        """
        retval = {'TARGETS': target, 'TARGET': target,
                  'CHANGED_TARGETS': '$TARGETS', 'UNCHANGED_TARGETS': '$TARGETS',
                  'SOURCES': source, 'SOURCE': source,
                  'CHANGED_SOURCES': '$SOURCES', 'UNCHANGED_SOURCES': '$SOURCES'}

        return retval



