import re

from collections import UserDict, UserList
from numbers import Number

from SCons.Util import is_String, is_Sequence, CLVar
from SCons.Subst import AllowableExceptions, raise_exception


_debug = True
if _debug:
    def debug(a):
        print(a)
else:
    def debug(a):
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

# This regular expression is used to replace strings of multiple white
# space characters in the string result from the scons_subst() function.
_space_sep = re.compile(r'[\t ]+(?![^{]*})')

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
    SHELL_REDIRECT = 11  # see SHELL_REDIRECT_CHARACTERS below
    NUMBER = 12
    LITERAL = 13  # This is a string which should be expanded no further.
    NONE = 14
    EVALUABLE = 15

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
               ]

    SHELL_REDIRECT_CHARACTERS = '<>|'

    @staticmethod
    def enum_name(value):
        return ValueTypes.strings[value]



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
    def __init__(self, value):
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

    def is_cached(self, env):
        return hasattr(self, 'cached')

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

                if len(self.value) == 1 and isinstance(self.value, (list, UserDict, tuple))\
                        and '$' not in self.value[0]:
                    # Short cut if we only have 1 value and it has no $'s
                    self.cached = (str(self.value[0]), str(self.value[0]))


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

                if '.' in value or '[' in value:
                    all_dependencies.append((ValueTypes.EVALUABLE, value, index))
                elif '(' in value:
                        # Parse call to see if we can determine other dependencies from parameters
                        self._parse_function_call_dependencies(value)
                        all_dependencies.append((ValueTypes.FUNCTION_CALL, value, index))
                else:
                    all_dependencies.append((ValueTypes.CALLABLE,v[2:-1], index))
            elif '.' in v:
                all_dependencies.append((ValueTypes.EVALUABLE, v[1:], index))
            else:
                # Plain Variable or callable. So label VARIABLE_OR_CALLABLE
                all_dependencies.append((ValueTypes.VARIABLE_OR_CALLABLE,v[1:], index))

        self.all_dependencies = all_dependencies

        # Dump out debug info
        self.debug_print_parsed_parts(all_dependencies)

        depend_list = [v for (t,v,i) in all_dependencies
                       if t in (ValueTypes.VARIABLE_OR_CALLABLE, ValueTypes.VARIABLE, ValueTypes.CALLABLE)]

        self.depends_on = self.depends_on.union(set(depend_list))

    @staticmethod
    def debug_print_parsed_parts(all_dependencies):
        for (index, val) in enumerate(all_dependencies):
            if val:
                (t, v, i) = val
                debug("[%4d] %20s, %5s, %s" % (index, ValueTypes.enum_name(t), i, v))
            else:
                debug("[%4d] %20s, %5s, %s" % (index,"None","None","None"))

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
                debug("Matching key:%s -> (%s/%s/%s)"%(key,ValueTypes.enum_name(t),v,i))

                if callable(all_values[key].value):
                    t = ValueTypes.CALLABLE
                else:
                    t = ValueTypes.VARIABLE

                debug("Now         :%s -> (%s/%s/%s)"%(key,ValueTypes.enum_name(t),v,i))

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

        try:
            s = to_call(target=lvars['TARGETS'],
                        source=lvars['SOURCES'],
                        env=gvars,
                        for_signature=for_sig)
        except TypeError as e:
            # TODO: Handle conv/convert parameters...
            s = str(to_call)
            raise Exception("Not handled eval_callable not normal params")

        # TODO: Now we should ensure the value from callable is then substituted as it can return $XYZ..

        return s

    def subst(self, env, mode=0, target=None, source=None, gvars={}, lvars={}, conv=None):
        """
        Expand string
        :param env:  EnvironmentValues providing context for this subst operation
        :param mode: 0 = leading or trailing white space will be removed from the result. and all sequences of white
                        space will be compressed to a single space character. Additionally, any $( and $) character
                        sequences will be stripped from the returned string
                    1 = preserve white space and $(-$) sequences.
                    2 = strip all characters between any $( and $) pairs (as is done for signature calculation)
                    Must be one of the SubstModes values.
        :param target: list of target Nodes
        :param source: list of source Nodes - Both target and source must be set if $TARGET, $TARGETS, $SOURCE and
                       $SOURCES are to be available for expansion
        :param conv: may specify a conversion function that will be used in place of the default. For example,
                     if you want Python objects (including SCons Nodes) to be returned as Python objects, you can use
                     the Python lambda idiom to pass in an unnamed function that simply returns its unconverted argument.
        :return: expanded string
        """

        for_signature = mode == SubstModes.FOR_SIGNATURE

        # TODO:Figure out how to handle this properly.  May involve seeing if source & targets is specified. Or checking
        #      against list of variables which are "ok" to leave undefined and unexpanded in the returned string and/or
        #      the cached values.  This is likely important for caching CCCOM where the TARGET/SOURCES will change
        #      and there is still much value in caching whatever else can be cached from such strings
        ignore_undefined = False

        use_cache_item = 0
        if for_signature:
            use_cache_item = 1

        try:
            return self.cached[use_cache_item]
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

            # Create pre-sized arrays to hold string values and non-string values.
            string_values = [None] * len(self.all_dependencies)
            parsed_values = [None] * len(self.all_dependencies)

            # Break parts in to simple strings or parts to be further evaluated
            for (t, v, i) in self.all_dependencies:
                if t not in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END, ValueTypes.STRING) and v in env \
                        and env[v].is_cached(env):
                    string_values[i] = (env[v].cached[use_cache_item], t)
                elif t in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                    string_values[i] = (v, t)
                elif t in (ValueTypes.VARIABLE, ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                    parsed_values[i] = (t,v,i)
                elif t == ValueTypes.CALLABLE:
                    # Put the actual value to be called in v, rather than the EnvironmentValue.
                    try:
                        v = lvars[v]
                    except KeyError as e:
                        v = env[v].value

                    parsed_values[i] = (t,v,i)
                elif t == ValueTypes.VARIABLE_OR_CALLABLE:
                    if v in env or v in lvars:
                        try:
                            if callable(lvars[v]):
                                t = ValueTypes.CALLABLE
                                v = lvars[v]
                            else:
                                t = ValueTypes.PARSED
                        except KeyError as e:
                            try:
                                if callable(env[v].value):
                                    t = ValueTypes.CALLABLE
                                    v = env[v].value
                                else:
                                    t = ValueTypes.PARSED
                            except KeyError as e:
                                t = ValueTypes.PARSED

                    parsed_values[i] = (t,v,i)
                else:
                    string_values[i] = (v, t)

            debug("Parsed values:%s  for %s [%s]"%(parsed_values, self._parsed, string_values))

            # Now we should be able to resolve if value is a callable or a variable.
            # if unsure, we'll leave as callable.
            for pv in parsed_values:
                if pv is None:
                    continue
                (t, v, i) = pv

                nt = t
                # We should be able to resolve now if it's a variable or a callable.
                if t == ValueTypes.EVALUABLE:
                    if '(' in v:
                        nt = ValueTypes.EVALUABLE
                    elif '.' not in v and '[' not in v:
                        nt = ValueTypes.PARSED
                        if v not in lvars and v in env:
                            nt = env[v].var_type
                        elif v in lvars:
                            nt = ValueTypes.PARSED # Should we have lvars type?
                        else:
                            if NameError not in AllowableExceptions:
                                raise_exception(NameError(v), lvars['TARGETS'], self.value)
                            else:
                                # It's ok to have an undefined variable. Just replace with blank.
                                string_values[i] = ''
                                parsed_values[i] = None

                    else:
                        # Something else where eval'ing it should suffice to yield a good value.
                        t = ValueTypes.EVALUABLE
                if nt != t:
                    # We've modified the type, so update parsed values
                    parsed_values[i] = (nt, v, i)

            debug("==============================")
            debug("After resolving unknown types:")
            self.debug_print_parsed_parts(parsed_values)

            # Now resolve all non-string values.
            while any(parsed_values):
                for pv in parsed_values:
                    if pv is None:
                        continue
                    (t,v,i) = pv


                    # # Below should only apply if it's a variable and it's not defined.
                    # # not for callables. callables can come from CALLABLE or VARIABLE_OR_CALLABLE
                    #
                    # if NameError not in AllowableExceptions:
                    #     raise_exception(NameError(v), lvars['TARGETS'], self.value)
                    # else:
                    #     # It's ok to have an undefined variable. Just replace with blank.
                    #     string_values[i] = ''
                    #     parsed_values[i] = None
                    #     continue

                    # At this point it's possible to determine if we guessed callable correctly
                    # or if it's actually evaluable
                    if t == ValueTypes.CALLABLE:
                        if callable(v):
                            t = ValueTypes.CALLABLE
                        else:
                            debug("Swapped to EVALUABLE:%s"%v)
                            t = ValueTypes.EVALUABLE


                    # Now handle all the various types which can be in the value.
                    if t == ValueTypes.CALLABLE:
                        to_call = v

                        call_value = self.eval_callable(to_call, parsed_values, string_values, target=target,
                                                        source=source, gvars=env, lvars=lvars, for_sig=for_signature)

                        # TODO: Handle return value not being a string, (a collection for example)

                        if is_String(call_value) and '$' not in call_value:
                            string_values[i] = (call_value,ValueTypes.STRING)
                        elif is_Sequence(call_value):
                            # TODO: Handle if need to put back in parsed_values.. (check for $ in any element)
                            # and/or call subst..
                            string_values[i] = (" ".join(call_value), ValueTypes.STRING)
                            part_string_value = []
                            for part in call_value:
                                if is_String(part) and '$' not in part:
                                    part_string_value.append(part)
                                else:
                                    try:
                                        part_string_value.append(env[part].subst(env, mode, target, source, gvars,
                                                                                 lvars, conv))
                                    except KeyError as e:
                                        ev = EnvironmentValue(call_value)
                                        string_values[i] = (
                                        ev.subst(env, mode, target, source, gvars, lvars, conv), ValueTypes.STRING)

                        else:
                            try:
                                string_values[i] = env[call_value].subst(env, mode, target, source, gvars, lvars, conv)
                            except KeyError as e:
                                ev = EnvironmentValue(call_value)
                                string_values[i] = (ev.subst(env, mode, target, source, gvars, lvars, conv), ValueTypes.STRING)

                        parsed_values[i] = None
                    elif t == ValueTypes.PARSED:
                        debug("PARSED   Type:%s VAL:%s"%(pv[0],pv[1]))

                        try:
                            try:
                                value = lvars[v]
                            except KeyError as e:
                                value = env[v].value

                            # Shortcut self reference
                            if isinstance(value, Number):
                                string_values[i] = (value, ValueTypes.NUMBER)
                            elif is_String(value) and len(value) >1 and value[0] == '$' and value[1:] == v:
                                # TODO: Is this worth doing? (Check line profiling once we get all functionality working)
                                # Special case, variables value references itself and only itself
                                string_values[i] = ('', ValueTypes.STRING)
                            else:
                                # TODO: Handle other recursive loops by empty stringing this value before recursing with copy of lvar?
                                string_values[i] = (env[v].subst(env, mode, target, source, gvars, lvars, conv),
                                                    ValueTypes.STRING)
                            debug("%s->%s" % (v,string_values[i]))
                        except KeyError as e:
                            # Must be lvar
                            if v[0] == '{' or '.' in v:
                                value = eval(v, gvars, lvars)
                            else:
                                value = str(lvars[v])

                            string_values[i] = (value, ValueTypes.STRING)
                        parsed_values[i] = None
                    elif t == ValueTypes.STRING:
                        # The variable resolved to a string . No need to process further.
                        debug("STR      Type:%s VAL:%s"%(pv[0],pv[1]))
                        string_values[i] = (env[v].value,t )
                        debug("%s->%s" % (v,string_values[i]))
                        parsed_values[i] = None
                    elif t == ValueTypes.NUMBER:
                        # The variable resolved to a number. No need to process further.
                        debug("Num      Type:%s VAL:%s"%(pv[0],pv[1]))
                        string_values[i] = (str(env[v].value), t)
                        debug("%s->%s" % (v,string_values[i]))
                        parsed_values[i] = None
                    elif t == ValueTypes.COLLECTION:
                        # Handle list, tuple, or dictionary
                        # Basically iterate all items, evaluating each, and then join them together with a space
                        debug("COLLECTION  Type:%s VAL:%s" % (t,v))
                        value = env[v].value

                        # TODO: Finish implementation
                        # This is very simple implementation which ignores nested collections and values which
                        # need to be further evaluated.(subst'd)
                        string_values[i] = (" ".join(value), t)
                        parsed_values[i] = None
                    elif t in (ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                        try:
                            # Note: this may return a callable or a string or a number or an object.
                            # If it's callable, then it needs be executed by the logic above for ValueTypes.CALLABLE.
                            sval = eval(v, gvars, lvars)
                        except AllowableExceptions as e:
                            sval = ''
                        if is_String(sval):
                            string_values[i] = (sval, ValueTypes.NUMBER)
                            parsed_values[i] = None
                        elif callable(sval):
                            parsed_values[i] = (ValueTypes.CALLABLE, sval, i)
                    elif t == ValueTypes.VARIABLE_OR_CALLABLE and v not in lvars and v not in gvars:
                        string_values[i] = ('', ValueTypes.STRING) # not defined so blank string
                        parsed_values[i] = None
                    else:
                        debug("AAHAHAHHAH BROKEN")
                        import pdb; pdb.set_trace()


            # Create and cache for signature if possible.
            in_escape_count = 0
            escape_values = []
            subst_string_values = []
            for (v, t) in string_values:
                sval = str(v)
                if not len(sval):
                    continue

                if t == ValueTypes.ESCAPE_START:
                    # Increase escape level.. allow wrapped escapes $( $( $x $) $)
                    in_escape_count +=1
                    continue
                elif t == ValueTypes.ESCAPE_END:
                    in_escape_count -= 1
                    continue
                elif in_escape_count > 0:
                    # Don't add to escape_values, but do add to string values
                    pass
                else:
                    escape_values.append(sval)

                subst_string_values.append(sval)

            subst_value = "".join(subst_string_values)

            # SubstModes.NORMAL we strip whitespace and remove duplicate whitespace
            # Compress strings of white space characters into
            # a single space.
            subst_value = _space_sep.sub(' ', subst_value).strip()

            if in_escape_count != 0:
                # TODO: Throw exception as unbalanced escapes
                pass

            signature_string = "".join(escape_values)

            # If mode = SubstModes.RAW we need to not do this.
            # TODO: Properly implement SubstModes.RAW
            signature_string = _space_sep.sub(' ', signature_string).strip()


            debug("HERE:%s  Escaped:%s"%(subst_value, signature_string))

            # Cache both values
            self.cached = (subst_value, signature_string)

            if not for_signature:
                return subst_value
            else:
                return signature_string
