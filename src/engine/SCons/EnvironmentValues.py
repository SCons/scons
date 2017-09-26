import re
from SCons.Util import is_String

from collections import UserDict, UserList

# try:
#     from UserDict import UserDict
# except ImportError as e:
#     from collections import UserDict
#
# try:
#     from UserList import UserList
# except ImportError as e:
#     from collections import UserList


_is_valid_var = re.compile(r'[_a-zA-Z]\w*$')

_rm = re.compile(r'\$[()]')
_remove = re.compile(r'\$\([^\$]*(\$[^\)][^\$]*)*\$\)')

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
_dollar_exps_str = r'\$[\$\(\)]|\$[_a-zA-Z][\.\w]*|\${[^}]*}'
_dollar_exps = re.compile(r'(%s)' % _dollar_exps_str)
_separate_args = re.compile(r'(%s|\s+|[^\s\$]+|\$)' % _dollar_exps_str)

# This regular expression is used to replace strings of multiple white
# space characters in the string result from the scons_subst() function.
_space_sep = re.compile(r'[\t ]+(?![^{]*})')


class ValueTypes(object):
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
    ESCAPE_START = 8
    ESCAPE_END = 9


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
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.var_type = ValueTypes.UNKNOWN
        self._parsed = []
        self.depends_on = set()

        self.set_value(name,value)

    def set_value(self, name, value):
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
            if self.var_type == ValueTypes.PARSED:
                self.find_dependencies()

    def __getitem__(self, item):
        return self.value

    def __setitem__(self, key, value):
        self.value[key] = value

    def is_cached(self, env):
        return hasattr(self,'cached')

    def parse_value(self):
        """
        Scan the string and break into component values
        """
        try:
            if is_String(self.value):
                self.var_type = ValueTypes.STRING

                if '$' in self.value:
                    # Now we need to parse the specified string
                    result = _separate_args.findall(self.value)
                    self._parsed = result
                    self.var_type = ValueTypes.PARSED
                    # print(result)
                elif self.value == ' ':
                    self.var_type = ValueTypes.SPACE
                else:
                    self.cached = self.value
            elif isinstance(self.value, (list, dict, tuple, UserDict, UserList)):
                # Not string and not a callable, Should be some value
                # like dict, tuple, list
                self.var_type = ValueTypes.COLLECTION
            pass
        except TypeError:
            # likely callable? either way we don't parse
            print("Value:%s"%self.value)

    @staticmethod
    def _parse_function_call_dependencies(item):
        """
        Parse a function all for all it's parameters.
        _stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)
        Should yield
        LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__
        Plus the function itself
        _stripixes
        :param item: subst string which is function call to be parsed
        :return: set of dependencies
        """
        retval = []

        function_name, remainder = item.split('(')

        retval.append((ValueTypes.CALLABLE,function_name))
        if remainder[-1] != ')':
            # This shouldn't happen raise Exception
            raise EnvironmentValueParseError("No closing paren parsing Environment value function call "+item)
        else:
            parameters = remainder[:-1].split(',')

        retval.extend([(ValueTypes.VARIABLE, v) for v in parameters])
        return retval

    def find_dependencies(self):
        """
        Find all the values which this value depends on (one layer deep)
        :return:
        """
        all_dependencies = []
        for v in self._parsed:
            # print("Processing [%s]"%v)

            if v == ' ':
                continue

            if len(v) == 1:  # Was v == ' '
                all_dependencies.append((ValueTypes.STRING, v))
                continue
            s0, s1 = v[:2]
            if s0 != '$':
                # Not a variable so we don't care
                all_dependencies.append((ValueTypes.STRING, v))
                continue
            if s0 == '$' and s1 == '(':
                # Escaping of value from signature calculations
                all_dependencies.append((ValueTypes.ESCAPE_START, v))
                continue
            if s0 == '$' and s1 == ')':
                # Escaping of value from signature calculations
                all_dependencies.append((ValueTypes.ESCAPE_END, v))
                continue

            if s1 == '$':
                # A literal dollar sign so we don't care
                all_dependencies.append((ValueTypes.STRING, s1))
                # continue
            if s1 == '{':
                # TODO: Must label as callable, or eval-able
                # This is a function call and/or requires python evaluation
                # Can be x.property or x(VAR1,VAR2)
                # If we can detect all info which affects this then we can cache
                value = v[2:-1]
                if '(' in value:
                    # Parse call to see if we can determine other dependencies from parameters
                    all_dependencies.extend(self._parse_function_call_dependencies(value))
                else:
                    all_dependencies.append((ValueTypes.CALLABLE,v[2:-1]))
            elif '.' in v:
                all_dependencies.append((ValueTypes.CALLABLE,v[1:]))
            else:
                # Plain Variable, capture it
                all_dependencies.append((ValueTypes.VARIABLE,v[1:]))

        self.all_dependencies = all_dependencies
        depend_list = [v for (t,v) in all_dependencies if t in (ValueTypes.VARIABLE, ValueTypes.CALLABLE)]
        self.depends_on = set(depend_list)
        # print("[%s] parsed:%s\n  Depends on:%s"%(self.name, self._parsed, self.depends_on))
        # print("--->%s"%all_dependencies)

    def subst(self, env, ignore_undefined=False, for_signature=False):
        """
        Expand string
        :param env:
        :param ignore_undefined: If we run into undefined value evaluating the string, should we error or continue
        :param for_signature: Are we expanding for use in signature
        :return:
        """


        try:
            if self.cached and not for_signature:
                return self.cached[0]
            else:
                return self.cached[1]
        except AttributeError as e:
            # We don't have a cached version yet, so generate the string

            missing_values = set()

            if not ignore_undefined:
                if self.depends_on != env.key_set:
                    # TODO: Raise error missing key
                    pass
            else:
                missing_values = self.depends_on - env.key_set

            # check all parts of value and see if any are PARSED (and not yet cached).
            #   If so add those to list and process that list (DO NOT RECURSE.. slow), also in working list, replace value
            #   with expanded parsed value
            # We should end up with a list of EnvironmentValue(s) (Not the object, just the plural)
            parsed_values = [v for (t,v) in self.all_dependencies if t in (ValueTypes.VARIABLE, ValueTypes.CALLABLE) and not env[v].is_cached(env)]
            string_values = [v for (t,v) in self.all_dependencies if t not in (ValueTypes.VARIABLE, ValueTypes.CALLABLE) or env[v].is_cached(env)]
            print("Parsed values:%s  for %s [%s]"%(parsed_values, self._parsed, string_values))

            while len(parsed_values) != 0:
                # TODO: expand parsed values
                pass


            # Handle undefined with some proper SCons exception
            subst_value = " ".join([env[v].value for (t,v) in self.all_dependencies if t not in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END)])

            # Create and cache for signature if possible.
            in_escape_count = 0
            escape_values = []
            for (t,v) in self.all_dependencies:
                if t == ValueTypes.ESCAPE_START:
                    # Increase escape level.. allow wrapped escapes $( $( $x $) $)
                    in_escape_count +=1
                elif t == ValueTypes.ESCAPE_END:
                    in_escape_count -= 1
                elif in_escape_count > 0:
                    # Skip value
                    continue
                else:
                    escape_values.append(env[v].value)

            if in_escape_count != 0:
                # TODO: Throw exception as unbalanced escapes
                pass

            signature_string = " ".join(escape_values)

            print("HERE:%s  Escaped:%s"%(subst_value, signature_string))

            # Cache both values
            self.cached = (subst_value, signature_string)

            if not for_signature:
                return subst_value
            else:
                return signature_string


class EnvironmentValues(object):
    """
    A class to hold all the environment variables
    """
    def __init__(self, **kw):
        self.values = {}
        for k in kw:
            self.values[k] = EnvironmentValue(k, kw[k])
        self.key_set = set(self.values.keys())


    def __setitem__(self, key, value):
        self.values[key] = EnvironmentValue(key, value)
        self.key_set.add(key)

    def __contains__(self, item):
        return item in self.values

    def __getitem__(self, item):
        return self.values[item]


    def subst(self, item, ignore_undefined=False, for_signature=False):
        """
        Recursively expand string for provided key
        :param item:
        :param ignore_undefined: If we run into undefined value evaluating the string, should we error or continue
        :param for_signature: Are we expanding for use in signature
        :return:
        """

        if self.values[item].var_type == ValueTypes.STRING:
            return self.values[item].value
        elif self.values[item].var_type == ValueTypes.PARSED:
            return self.values[item].subst(self, ignore_undefined, for_signature)