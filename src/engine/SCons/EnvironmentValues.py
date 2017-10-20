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
    ESCAPE_START = 8  # $(
    ESCAPE_END = 9    # $)
    VARIABLE_OR_CALLABLE = 10

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
               'VARIABLE_OR_CALLABLE']

    @staticmethod
    def enum_name(value):
        return ValueTypes.strings[value]


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
        all_dependencies = []

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
                    self.cached = (self.value, self.value)
            elif isinstance(self.value, (list, dict, tuple, UserDict, UserList)):
                # Not string and not a callable, Should be some value
                # like dict, tuple, list
                self.var_type = ValueTypes.COLLECTION
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
            self.depends_on.add(p)

        return parameters

    def find_dependencies(self):
        """
        Find all the values which this value depends on (one layer deep)
        :return:
        """
        all_dependencies = []
        skipped = 0  # count the number of skipped blank spaces
        for i, v in enumerate(self._parsed):
            # print("Processing [%s]"%v)

            if v == ' ':
                skipped += 1
                continue

            # index for all_dependencies adjusted to account for values we skipped from self._parsed
            index = i - skipped

            if len(v) == 1:  # Was v == ' '
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
                # continue
            if s1 == '{':
                # TODO: Must label as callable, or eval-able
                # This is a function call and/or requires python evaluation
                # Can be x.property or x(VAR1,VAR2)
                # If we can detect all info which affects this then we can cache
                value = v[2:-1]

                if '(' in value:
                    # Parse call to see if we can determine other dependencies from parameters
                    self._parse_function_call_dependencies(value)
                    all_dependencies.append((ValueTypes.FUNCTION_CALL, value, index))
                else:
                    all_dependencies.append((ValueTypes.CALLABLE,v[2:-1], index))
            elif '.' in v:
                all_dependencies.append((ValueTypes.CALLABLE,v[1:], index))
            else:
                # Plain Variable or callable. So label VARIABLE_OR_CALLABLE
                all_dependencies.append((ValueTypes.VARIABLE_OR_CALLABLE,v[1:], index))

        self.all_dependencies = all_dependencies

        dl = []

        for (t,v,i) in all_dependencies:
            print("%20s, %5s, %s"%(ValueTypes.enum_name(t),i,v))

        depend_list = [v for (t,v,i) in all_dependencies
                       if t in (ValueTypes.VARIABLE_OR_CALLABLE, ValueTypes.VARIABLE, ValueTypes.CALLABLE)]

        self.depends_on = self.depends_on.union(set(depend_list))

    def create_local_var_dict(self, target, source):
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

    def eval_callable(self, to_call, parsed_values, string_values,
                      target=None, source=None, gvars={}, lvars={}, for_sig=False):
        """
        Evaluate a callable and return the generated string.
        (Note we'll need to handle recursive expansion)
        :param to_call: The callable to call..
        :param gvars:
        :param lvars:
        :return:
        """

        if 'TARGET' not in lvars:
            d = self.create_local_var_dict(target, source)
            if d:
                lvars = lvars.copy()
                lvars.update(d)

        s = to_call(target=lvars['TARGETS'],
              source=lvars['SOURCES'],
              env=gvars,
              for_signature=for_sig)

        return s

    def subst(self, env, raw=0, target=None, source=None, gvars={}, lvars={}, conv=None):
        """
        Expand string
        :param env:
        :param raw: 0 = leading or trailing white space will be removed from the result. and all sequences of white
                        space will be compressed to a single space character. Additionally, any $( and $) character
                        sequences will be stripped from the returned string
                    1 = preserve white space and $(-$) sequences.
                    2 = strip all characters between any $( and $) pairs (as is done for signature calculation)
        :param target: list of target Nodes
        :param source: list of source Nodes - Both target and source must be set if $TARGET, $TARGETS, $SOURCE and
                       $SOURCES are to be available for expansion
        :param conv: may specify a conversion function that will be used in place of the default. For example,
                     if you want Python objects (including SCons Nodes) to be returned as Python objects, you can use
                     the Python lambda idiom to pass in an unnamed function that simply returns its unconverted argument.
        :return: expanded string
        """

        for_signature = raw == SubstModes.FOR_SIGNATURE

        # TODO: Figure out how to handle this properly.  May involve seeing if source & targets is specified. Or checking
        #       against list of variables which are "ok" to leave undefined and unexpanded in the returned string and/or
        #       the cached values.  This is likely important for caching CCCOM where the TARGET/SOURCES will change
        #       and there is still much value in caching whatever else can be cached from such strings
        ignore_undefined = False

        use_cache_item = 0
        if for_signature:
            use_cache_item = 1

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
                    # TODO: May want to make sure the difference also doesn't match TARGET,TARGETS,SOURCE,SOURCES, etc..
                    pass
            else:
                missing_values = self.depends_on - env.key_set

            # check all parts of value and see if any are PARSED (and not yet cached).
            #   If so add those to list and process that list (DO NOT RECURSE.. slow), also in working list,
            #   replace value with expanded parsed value
            # We should end up with a list of EnvironmentValue(s) (Not the object, just the plural)
            # parsed_values = [v for (t, v, i) in self.all_dependencies
            #                  if t in (ValueTypes.VARIABLE, ValueTypes.CALLABLE) and not env[v].is_cached(env)]
            # string_values = [v for (t, v, i) in self.all_dependencies
            #                  if t not in (ValueTypes.VARIABLE, ValueTypes.CALLABLE) or env[v].is_cached(env)]
            # print("Parsed values:%s  for %s [%s]"%(parsed_values, self._parsed, string_values))

            # Create pre-sized arrays to hold string values and non-string values.
            string_values = [None] * len(self.all_dependencies)
            parsed_values = [None] * len(self.all_dependencies)

            for (t, v, i) in self.all_dependencies:
                if t not in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END, ValueTypes.STRING) and env[v].is_cached(env):
                    string_values[i] = (env[v].cached[use_cache_item], t)
                elif t in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                    string_values[i] = (v, t)
                elif t in (ValueTypes.VARIABLE, ValueTypes.CALLABLE, ValueTypes.VARIABLE_OR_CALLABLE):
                    parsed_values[i] = (t,v,i)
                else:
                    string_values[i] = (v, t)

            print("Parsed values:%s  for %s [%s]"%(parsed_values, self._parsed, string_values))

            # Now resolve all non-string values.
            while any(parsed_values):
                # TODO: expand parsed values
                for pv in parsed_values:
                    if pv is None:
                        continue
                    (t,v,i) = pv

                    # We should be able to resolve now if it's a variable or a callable.
                    if t == ValueTypes.VARIABLE_OR_CALLABLE:
                        t = env[v].var_type

                    if t == ValueTypes.CALLABLE:
                        to_call = env[v].value
                        string_values[i] = (self.eval_callable(to_call, parsed_values, string_values, target=target,
                                                               source=source, gvars=env, lvars={}, for_sig=for_signature),
                                            ValueTypes.STRING)
                        print("CALLABLE VAL:%s->%s"%(pv[1], string_values[i]))
                        parsed_values[i] = None
                    elif t == ValueTypes.PARSED:
                        print("PARSED   Type:%s VAL:%s"%(pv[0],pv[1]))
                        string_values[i] = (env[v].subst(env, raw, target, source, gvars, lvars, conv),
                                            ValueTypes.STRING)
                        print("%s->%s" % (v,string_values[i]))
                        parsed_values[i] = None
                    else:
                        print("AAHAHAHHAH BROKEN")

            # Handle undefined with some proper SCons exception
            subst_value = " ".join([v for (v, t) in string_values if t not in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END)])

            # Create and cache for signature if possible.
            in_escape_count = 0
            escape_values = []
            for (v, t) in string_values:
                if t == ValueTypes.ESCAPE_START:
                    # Increase escape level.. allow wrapped escapes $( $( $x $) $)
                    in_escape_count +=1
                elif t == ValueTypes.ESCAPE_END:
                    in_escape_count -= 1
                elif in_escape_count > 0:
                    # Skip value
                    continue
                else:
                    escape_values.append(v)

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

    def subst(self, item, raw=0, target=None, source=None, gvars={}, lvars={}, conv=None):
        """
        Recursively Expand string
        :param env:
        :param raw: 0 = leading or trailing white space will be removed from the result. and all sequences of white
                        space will be compressed to a single space character. Additionally, any $( and $) character
                        sequences will be stripped from the returned string
                    1 = preserve white space and $(-$) sequences.
                    2 = strip all characters between any $( and $) pairs (as is done for signature calculation)
        :param target: list of target Nodes
        :param source: list of source Nodes - Both target and source must be set if $TARGET, $TARGETS, $SOURCE and
                       $SOURCES are to be available for expansion
        :param conv: may specify a conversion function that will be used in place of the default. For example,
                     if you want Python objects (including SCons Nodes) to be returned as Python objects, you can use
                     the Python lambda idiom to pass in an unnamed function that simply returns its unconverted argument.
        :param gvars: Specify the global variables. Defaults to empty dict, which will yield using this EnvironmentValues
                      symbols.
        :param lvars: Specify local variables to evaluation the variable with. Usually this is provided by executor.
        :return: expanded string
        """

        if not gvars:
            gvars = self.values

        # TODO: Fill in gvars, lvars as env.Subst() does..

        if self.values[item].var_type == ValueTypes.STRING:
            return self.values[item].value
        elif self.values[item].var_type == ValueTypes.PARSED:
            return self.values[item].subst(self, raw=raw, target=target, source=source, gvars=gvars, lvars=lvars, conv=conv)
        elif self.values[item].var_type == ValueTypes.CALLABLE:
            # From Subst.py
            # try:
            #     s = s(target=lvars['TARGETS'],
            #           source=lvars['SOURCES'],
            #           env=self.env,
            #           for_signature=(self.mode != SUBST_CMD))
            # except TypeError:
            #     # This probably indicates that it's a callable
            #     # object that doesn't match our calling arguments
            #     # (like an Action).
            #     if self.mode == SUBST_RAW:
            #         return s
            #     s = self.conv(s)
            # return self.substitute(s, lvars)
            retval = self.values[item].value(target, source, self, (raw == 2))
            return retval
