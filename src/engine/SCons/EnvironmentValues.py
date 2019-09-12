import re
from numbers import Number

from SCons.Util import is_String, is_Sequence, CLVar, flatten
from SCons.Subst import CmdStringHolder, create_subst_target_source_dict, raise_exception
from SCons.EnvironmentValue import EnvironmentValue, ValueTypes, separate_args, SubstModes
import SCons.Environment

# import pysnooper

# AllowableExceptions = (IndexError, NameError)

# TODO: allow updating similar to Subst.SetAllowableExceptions()
AllowableExceptions = (KeyError,)

# _is_valid_var = re.compile(r'[_a-zA-Z]\w*$')
#
# _rm = re.compile(r'\$[()]')
# _remove = re.compile(r'\$\([^\$]*(\$[^\)][^\$]*)*\$\)')

# This regular expression is used to replace strings of multiple white
# space characters in the string result from the scons_subst() function.
space_sep = re.compile(r'[\t ]+(?![^{]*})')

_debug = False
if _debug:
    def debug(fmt, *args):
        # format when needed
        print(fmt % args)
else:
    # avoid any formatting overhead
    def debug(*unused):
        pass


def remove_escaped_items_from_list(list):
    """
    Returns list with all items inside escapes ( $( and $) )removed
    :param list:
    :return: list.
    """
    result = []
    depth = 0
    for l, t in list:
        if l == '$(':
            depth += 1
        elif l == '$)':
            depth -= 1
            if depth < 0:
                break
        elif depth == 0:
            result.append((l, t))
    if depth != 0:
        return None
    return result


class ParsedEnvironmentValue(object):
    """
    Hold information about values which are considered parsed (typically hold a variable and have a $ in them)
    """
    __slots__ = ['value', 'type', 'position', 'lvars']

    def __init__(self, type, value, position, lvars=None):
        """

        :param value:
        :param type:
        :param position:
        :param lvars:
        """
        self.value = value
        self.type = type
        self.position = position
        self.lvars = lvars

    def __str__(self):
        return "Type:%s VAL:%s"%(self.type, self.value)

    def resolve_unassigned_types(self, env_vals, gvars):
        """
        If the ParsedEnvironmentValue is not determined to be Callable or Variable yet, do so now.
        :param env_vals: The EnvironmentValues instance we're being called from
        :param gvars: Global variables
        :return: 0 - No change, 1 - Changed, 2 - Move to string_values and clear
        """

        nt = self.type

        # Resolve whether callable or a variable
        if self.type == ValueTypes.VARIABLE_OR_CALLABLE:
            if self.value in self.lvars:
                if callable(self.lvars[self.value]):
                    nt = ValueTypes.CALLABLE
                else:
                    nt = ValueTypes.PARSED
            elif self.value in gvars:
                if callable(gvars[self.value]):
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
                if self.value not in self.lvars and self.value in env_vals:
                    # Something like ${VARIABLE}
                    nt = env_vals[self.value].var_type
                elif self.value in self.lvars:
                    nt = ValueTypes.PARSED  # Should we have lvars type?
                else:
                    if NameError not in AllowableExceptions:
                        raise_exception(NameError(self.value), self.lvars['TARGETS'], self.value)
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


class EnvironmentValues(object):
    """
    A class to hold all the environment variables
    """

    def __init__(self, **kw):
        self.values = dict((k, EnvironmentValue(v)) for k, v in kw.items())
        self._dict = kw.copy()
        self.key_set = set(kw.keys())
        self.cached_values = {}

    def __setitem__(self, key, value):
        debug("SETITEM:[%s]%s->%s", id(self), key, value)
        self.values[key] = EnvironmentValue(value)
        self._dict[key] = value

        self.key_set.add(key)

        # TODO: Now reevaluate any keys which depend on this value for better caching?
        self.update_cached_values(key)

    def __contains__(self, item):
        return item in self.values

    def __getitem__(self, item):
        return self.values[item]

    def Dictionary(self, *args):
        """
        Create a dictionary we can pass to eval().
        :param args:
        :return: dictionary of strings and their values.
        """
        if not args:
            return self._dict
        dlist = [self._dict[x] for x in args]
        if len(dlist) == 1:
            dlist = dlist[0]
        return dlist

    def update_cached_values(self, key):
        """
        Key has been set/changed. We need to effectively flush the cached subst values
        (If there are any).
        Also we may change the type of parsed parts of values.

        TODO: Does this need to recursively be re-evaluated?

        :param key: The changed key in the environment.
        :return: None.
        """

        # Find all variables which depend on the key

        # to_update = set([v for v in self.values if key in self.values[v].depends_on])
        to_update = set([k for k, v in self.values.items() if key in v.depends_on])

        # then recursively find all the other EnvironmentValue depending on
        # any keys which depend on the EnvironmentValue which depend on the key

        count = 0
        while to_update:

            # Create a list of all values which need to be update by our current list
            # of to_update variables. This should recursively give us a list of
            # all variables invalidated by the key being changed.

            next_to_update = set([k for k, v in self.values.items()
                                  for u in to_update
                                  #  k not in u ??? or  k != u ???
                                  if k not in u and u in v.depends_on])
            if not next_to_update:
                break

            to_update.update(next_to_update)

            debug("Pass [%6d]", count)
            count += 1

        for k in to_update:
            self.values[k].update(key, self.values)

    @staticmethod
    def split_dependencies(value, string_values, parsed_values, lvars,  reserved_name_set):
        """
        Split the dependencies for the value into strings and items which need further processing
        (parsed_values
        :param string_values:
        :param parsed_values:
        :return:
        """

        # Break parts in to simple strings or parts to be further evaluated
        for (t, v, i) in value.all_dependencies:
            if t in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                string_values[i] = (v, t)
            elif t in (ValueTypes.VARIABLE, ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                parsed_values[i] = ParsedEnvironmentValue(t, v, i, lvars)
            elif t == ValueTypes.CALLABLE:
                parsed_values[i] = ParsedEnvironmentValue(t, v, i, lvars)
            elif t == ValueTypes.VARIABLE_OR_CALLABLE:
                parsed_values[i] = ParsedEnvironmentValue(t, v, i, lvars)
            else:
                string_values[i] = (v, t)

        debug("Parsed values:%s  for %s [%s]" % (parsed_values, value._parsed, string_values))

    def resolve_unassigned_types(self, parsed_values, string_values, gvars, lvars):
        """
        Use the context to remove uncertainty on types
        :param parsed_values:
        :param gvars:
        :param lvars:
        :return:
        """

        # Now we should be able to resolve if value is a callable or a variable.
        # if unsure, we'll leave as callable.
        for pv in parsed_values:
            if pv is None:
                continue
            rv = pv.resolve_unassigned_types(self, gvars)
            if rv == 2:
                # It's ok to have an undefined variable. Just replace with blank.
                string_values[i] = ''
                parsed_values[i] = None

        debug("==============================")
        debug("After resolving unknown types:")
        EnvironmentValue.debug_print_parsed_parts(parsed_values)

    # @pysnooper.snoop()
    def evaluate_parsed_values(self, parsed_values, string_values, source, target, gvars, lvars, mode, conv=None):
        """
        Walk the list of parsed values and evaluate each in turn.  Possible return values for each are:
        * A plain string (No $ values)
        * A non-plain string (requires parsing and evaluation)
        * A collection of values (all plain strings)
        * A collection of values (not ALL plain strings)
        * Callable object

        :param parsed_values: An array containing ParsedEnvironmentValue objects or None
        :param string_values: An array of strings
        :param gvars:
        :param lvars:
        :return:
        """

        for_signature = mode == SubstModes.FOR_SIGNATURE

        new_parsed_values = []
        new_string_values = []
        for index, pv in enumerate(parsed_values[:]):

            # In the case there are any values in string_values, and any parsed_values are None
            # ensure we are not losing the existing string_values.
            if pv is None:
                new_parsed_values.append(None)
                new_string_values.append(string_values[index])
                continue

            # (t, v, i) = pv

            # TODO: # Below should only apply if it's a variable and it's not defined.
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
            # if t == ValueTypes.CALLABLE:
            #     if callable(v):
            #         t = ValueTypes.CALLABLE
            #     else:
            #         debug("Swapped to EVALUABLE:%s" % v)
            #         t = ValueTypes.EVALUABLE

            # Now handle all the various types which can be in the value.
            if pv.type == ValueTypes.STRING:
                # should yield a single value

                # The variable resolved to a string . No need to process further.
                debug("STR      %s" % pv)
                new_string_values.append((pv.value, pv.type))
                new_parsed_values.append(None)
                debug("%s->%s" % (pv.value, string_values[pv.position]))

            elif pv.type == ValueTypes.PARSED:
                # Can be multiple values
                debug("PARSED   %s"%pv)

                try:
                    # Now get an EnvironmentValue object to continue processing.
                    try:
                        value = EnvironmentValue.factory(pv.lvars[pv.value])
                    except KeyError as e:
                        value = self.values[pv.value]

                    # Now use value.var_type to decide how to proceed.
                    if value.var_type == ValueTypes.NUMBER:
                        new_string_values.append((value, ValueTypes.NUMBER))
                        new_parsed_values.append(None)

                    elif value.var_type == ValueTypes.STRING:
                        self_ref_location = value.value.find(pv.value)
                        if self_ref_location != -1 and value.value[self_ref_location-1] == '$':
                            #
                            pass

                        if len(value.value) > 1 and value.value[0] == '$' and value.value[1:] == pv.value:
                            # Special case, variables value references itself and only itself
                            new_string_values.append(('', ValueTypes.STRING))
                            new_parsed_values.append(None)
                        else:
                            new_string_values.append((value.value, ValueTypes.STRING))
                            new_parsed_values.append(None)
                    # elif value.var_type == ValueTypes.PARSED and value.value[0] == '$' and value.value[1:] == pv.value:
                    #     # TODO: need to check if any of the parts of this string have $ and match the current value
                    #     #  name so value.value = 'a $NAME b' where pv.value=='NAME'
                    #
                    #     # Handle when the value of the current value is a self reference 'R'='$R'.
                    #     # This prevents infinite recursion during evaluation and mimics previous
                    #     # functionality
                    #     new_string_values.append(('', ValueTypes.STRING))
                    #     new_parsed_values.append(None)
                    else:
                        # TODO: Handle other recursive loops by empty stringing this value before recursing with
                        #  copy of lvar?
                        npv = []
                        nsv = []
                        for (t, v, i) in value.all_dependencies:
                            pv.lvars = pv.lvars.copy()
                            pv.lvars[pv.value] = ''

                            if v == pv.value:
                                npv.append(None)
                                nsv.append(('', ValueTypes.STRING))
                                # pv.lvars = pv.lvars.copy()
                                # pv.lvars[pv.value] = ''
                            else:
                                npv.append(ParsedEnvironmentValue(t, v, i, pv.lvars))
                                nsv.append(None)

                        new_parsed_values.extend(npv)
                        new_string_values.extend(nsv)
                        # new_parsed_values.extend([ParsedEnvironmentValue(t, v, i, lvars) for (t, v, i) in value.all_dependencies])
                        # new_string_values.extend([None] * len(value.all_dependencies))

                    debug("%s->%s" % (pv.value, string_values[pv.position]))
                except KeyError as e:
                    if KeyError in AllowableExceptions:
                        new_string_values.append(('', ValueTypes.STRING))
                        new_parsed_values.append(None)

            elif pv.type == ValueTypes.CALLABLE:
                # Can return multiple values
                # TODO: What should V be. If it's a function it seems the name ends up in v, but if callable class
                #    v ends up being an instance of the callable class.  Both of which can return another callable
                #    or a string which requires further processing, or a plain string, or blank.
                if pv.value in self.values:
                    to_call = self.values[pv.value].value
                elif pv.value in lvars:
                    to_call = pv.lvars[pv.value]
                else:
                    print("Couldn't find key :%s" % pv.value)
                    to_call = pv.value

                call_value = self.eval_callable(to_call, parsed_values, string_values,
                                                target=lvars['TARGETS'],
                                                source=lvars['SOURCES'],
                                                gvars=gvars, lvars=lvars, mode=mode,
                                                conv=conv)

                new_values = []
                if is_String(call_value):
                    if '$' not in call_value:
                        new_string_values.append((call_value, ValueTypes.STRING))
                        new_parsed_values.append(None)

                        continue
                    else:
                        # TODO: Is this the right thing to do when the value is someting like
                        # ${CMDGEN('foo',0)}
                        value = EnvironmentValue.factory(call_value)
                        new_values.append(value)
                elif is_Sequence(call_value):
                    for val in call_value:
                        new_values.append(EnvironmentValue.factory(val))

                insert_count = 0
                # TODO: handle inserting/overwriting value and then inserting after that inplace thereafter
                for val in new_values:
                    # Now use value.var_type to decide how to proceed.
                    if val.var_type == ValueTypes.NUMBER:
                        new_string_values.append((val, ValueTypes.NUMBER))
                        new_parsed_values.append(None)

                    elif val.var_type == ValueTypes.STRING:
                        if val[0] == '$' and val[1:] == pv.value:
                            # Special case, variables value references itself and only itself
                            new_string_values.append(('', ValueTypes.STRING))
                            new_parsed_values.append(None)

                        else:
                            new_string_values.append((val.value, ValueTypes.STRING))
                            new_parsed_values.append(None)

                    else:
                        # TODO: Handle other recursive loops by empty stringing this value before recursing with copy of lvar?
                        new_parsed_values.extend(val.all_dependencies)
                        new_string_values.extend([None] * len(val.all_dependencies))

                # # TODO: Handle return value not being a string, (a collection for example)
                #

            elif pv.type == ValueTypes.NUMBER:
                # yields single value

                # The variable resolved to a number. No need to process further.
                debug("Num      %s"%pv)
                debug("%s->%s" % (pv.value, (str(env[pv.value].value), t)))
                new_string_values.append(str(env[pv.value].value), t)
                new_parsed_values.append(None)

            elif pv.type == ValueTypes.COLLECTION:
                # TODO:  How many values?

                # Handle list, tuple, or dictionary
                # Basically iterate all items, evaluating each, and then join them together with a space
                debug("COLLECTION  %s"%pv)
                value = env[pv.value].value

                # TODO: Finish implementation
                # This is very simple implementation which ignores nested collections and values which
                # need to be further evaluated.(subst'd)

                new_string_values.append((" ".join(value), t))
                new_parsed_values.append(None)

            elif pv.type in (ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                # Can yield multiple values

                try:
                    # Note: this may return a callable or a string or a number or an object.
                    # If it's callable, then it needs be executed by the logic above for ValueTypes.CALLABLE.
                    # TODO Fix gvars to have contents of variables rather than evaluating to EnvironmentValue object...
                    sval = eval(pv.value, gvars, lvars)
                except AllowableExceptions as e:
                    sval = ''

                if is_String(sval):
                    new_string_values.append((sval, ValueTypes.NUMBER))
                    new_parsed_values.append(None)

                elif callable(sval):
                    new_parsed_values.append((ValueTypes.CALLABLE, sval, i))
                    new_string_values.append(None)

            elif pv.type == ValueTypes.VARIABLE_OR_CALLABLE and pv.value not in pv.lvars and pv.value not in gvars:
                # Handle when variable is NOT defined by having blank string
                new_string_values.append(('', ValueTypes.STRING))
                new_parsed_values.append(None)

            elif pv.type in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                # Propagate escapes into string_values. Escaping is not done here.
                new_string_values.append((pv.value, pv.type))
                new_parsed_values.append(None)

            else:
                # SHOULD NEVER GET HERE. Drop into debugger if so.
                debug("AAHAHAHHAH BROKEN")
                # import pdb; pdb.set_trace()

        # Now correct index # for each item in new_parsed_values
        for (i, pv) in enumerate(new_parsed_values):
            if pv is not None:
                pv.position = i

        parsed_values = [pv is not None and pv or None for (i, pv) in enumerate(new_parsed_values)]
        string_values = new_string_values
        return parsed_values, string_values

    def eval_callable(self, to_call, parsed_values, string_values,
                      target=None, source=None, gvars={}, lvars={}, mode=SubstModes.RAW, conv=None):
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
                        env=self,
                        for_signature=(mode == SubstModes.FOR_SIGNATURE))
        except TypeError as e:
            # TODO: Handle conv/convert parameters...
            if mode != SubstModes.RAW:
                s = conv(to_call)
            else:
                s = to_call
            # raise Exception("Not handled eval_callable not normal params :%s"%s)

        # TODO: Now we should ensure the value from callable is then substituted as it can return $XYZ..

        return s

    @staticmethod
    def subst(substString, env, mode=0, target=None, source=None, gvars={}, lvars={}, conv=None):
        """
        Recursively Expand string
        :param substString: The string to be expanded.
        :param env:
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
        :param gvars: Specify the global variables. Defaults to empty dict, which will yield using this EnvironmentValues
                      symbols.
        :param lvars: Specify local variables to evaluation the variable with. Usually this is provided by executor.
        :return: expanded string
        """
        # subst called with plain string, just return it.
        if '$' not in substString:
            if mode != SubstModes.SUBST_LIST:
                return substString
            else:
                return [(substString, ValueTypes.STRING)]

        # TODO: Case to shortcut.  substString = "$VAR" and env['VAR'] = simple string.
        #  This happens enough to make it worth optimizing
        # if ' ' not in substString and substString[0]=='$' and

        # TODO:Figure out how to handle this properly.  May involve seeing if source & targets is specified. Or checking
        #      against list of variables which are "ok" to leave undefined and unexpanded in the returned string and/or
        #      the cached values.  This is likely important for caching CCCOM where the TARGET/SOURCES will change
        #      and there is still much value in caching whatever else can be cached from such strings
        ignore_undefined = False

        use_cache_item = 0
        if mode == SubstModes.FOR_SIGNATURE:
            use_cache_item = 1

        if not gvars:
            gvars = env._dict

        overrides = set()
        if lvars:
            # keys in lvars is going to be overrides
            overrides = overrides.union(lvars.keys())

            # remove reserved vars from the list
            overrides -= SCons.Environment.reserved_construction_var_names_set

        if 'TARGET' not in lvars:
            d = create_subst_target_source_dict(target, source)
            if d:
                lvars = lvars.copy()
                lvars.update(d)

        # Stick the element in a list, evaluate all elements in list until empty/all evaluated.
        # If evaluation returns a list from a single element insert that new list at the point the element
        # being evaluated was previously at.

        try:
            # First retrieve the value by substString and the applicable overrides.
            # TODO: Transpose overrides set into something which is cacheable. String for now, but maybe tuple instead?
            override_string = "-".join(sorted(overrides))

            val = env.cached_values[(substString, override_string)]
        except KeyError as e:
            # No such value create one
            val = EnvironmentValue.factory(substString)

        string_values = [None] * len(val.all_dependencies)
        parsed_values = [None] * len(val.all_dependencies)

        env.split_dependencies(val, string_values, parsed_values, lvars,
                               SCons.Environment.reserved_construction_var_names_set)


        # Ensure we don't go into an infinite loop of subst evaluations.
        iter_count=0
        while any(parsed_values):
            # Now we can use the context (env, gvars, lvars) to decide
            # any uncertain types in parsed_values
            env.resolve_unassigned_types(parsed_values, string_values, gvars, lvars)

            # Now evaluate the parsed values. Note that some of these may expand into
            # multiple values and require expansion of parsed_values and string_values array
            (parsed_values, string_values) = env.evaluate_parsed_values(parsed_values, string_values, source, target,
                                                                        gvars, lvars, mode, conv)
            iter_count +=1
            if iter_count > 12:
                raise Exception("Too many iterations in subst() bailing out")

        # Now handle subst mode during string expansion.
        if mode == SubstModes.SUBST_LIST:
            return string_values
        elif mode == SubstModes.FOR_SIGNATURE:
            string_values = remove_escaped_items_from_list(string_values)
        elif mode == SubstModes.NORMAL:
            string_values = [(s, t) for (s, t) in string_values if s not in ('$(', '$)')]
        # else Remaining mode is RAW where we don't strip anything.

        retval = " ".join([s for s, t in string_values])

        if mode in (SubstModes.FOR_SIGNATURE, SubstModes.NORMAL):
            retval = space_sep.sub(' ', retval).strip()

        return retval
        # try:
        #     var_type = env.values[substString].var_type
        #
        #     if var_type == ValueTypes.STRING:
        #         return env.values[substString].value
        #     elif var_type == ValueTypes.PARSED:
        #         return env.values[substString].subst(env, mode=mode, target=target, source=source, gvars=gvars,
        #                                              lvars=lvars, conv=conv)
        #     elif var_type == ValueTypes.CALLABLE:
        #         # From Subst.py
        #         # try:
        #         #     s = s(target=lvars['TARGETS'],
        #         #           source=lvars['SOURCES'],
        #         #           env=self.env,
        #         #           for_signature=(self.mode != SUBST_CMD))
        #         # except TypeError:
        #         #     # This probably indicates that it's a callable
        #         #     # object that doesn't match our calling arguments
        #         #     # (like an Action).
        #         #     if self.mode == SUBST_RAW:
        #         #         return s
        #         #     s = self.conv(s)
        #         # return self.substitute(s, lvars)
        #         # TODO: This can return a non-plain-string result which needs to be further processed.
        #         retval = env.values[substString].value(target, source, env, (mode == SubstModes.FOR_SIGNATURE))
        #         return retval
        # except KeyError as e:
        #     if is_String(substString):
        #         # The value requested to be substituted doesn't exist in the EnvironmentVariables.
        #         # So, let's create a new value?
        #         # Currently we're naming it the same as it's content.
        #         # TODO: Should we keep these separate from the variables? We're caching both..
        #         env.values[substString] = EnvironmentValue(substString)
        #         return env.values[substString].subst(env, mode=mode, target=target, source=source, gvars=gvars,
        #                                              lvars=lvars, conv=conv)
        #     elif is_Sequence(substString):
        #         return [EnvironmentValue(v).subst(env, mode=mode, target=target, source=source, gvars=gvars,
        #                                           lvars=lvars, conv=conv) for v in substString]


    @staticmethod
    def process_subst_modes(list_subst_results, mode):
        """
        Return escaped array of string results
        :param list_subst_results: post subst'd list of strings
        :param mode - SubstValue type (indicating what we should do with signature escapes $( and $)
        :return: escape processed array of strings
        """

        retval = []
        escape_level = 0
        for line_no, line in enumerate(list_subst_results):
            retval.append([])
            for item in line:
                parts = []
                for item_part, ip_type in item:
                    if ip_type == ValueTypes.ESCAPE_START:
                        escape_level += 1
                        if mode != SubstModes.RAW:
                            continue
                    elif ip_type == ValueTypes.ESCAPE_END:
                        escape_level -= 1
                        if mode != SubstModes.RAW:
                            continue

                    if escape_level > 0 and mode == SubstModes.FOR_SIGNATURE:
                        continue

                    parts.append(item_part)

                word = []
                for p in parts:
                    if p == '':
                        continue
                    elif p.isspace() and word:
                        retval[line_no].append("".join(word))
                        word = []
                    elif not p.isspace():
                        word.append(p)

                if word:
                    retval[line_no].append("".join(word))

                # if parts and len(parts) >= 1 and parts[0] != '':  # or mode == SubstModes.RAW:
                #     retval[line_no].append("".join(parts))
                # else:
                #     pass
        return retval



    @staticmethod
    def subst_list(listSubstVal, env, mode=SubstModes.RAW,
                   target=None, source=None, gvars={}, lvars={}, conv=None):
        """Substitute construction variables in a string (or list or other
        object) and separate the arguments into a command list.

        The companion subst() function (above) handles basic substitutions within strings, so see
        that function instead if that's what you're looking for.

        :param listSubstVal: Either a string (potentially with embedded newlines),
                     or a list of command line arguments.
        :param env:
        :param mode:
        :param target:
        :param source:
        :param gvars:
        :param lvars:
        :param conv:
        :return:  a list of lists of substituted values (First dimension is separate command line,
                  second dimension is "words" in the command line)

        """
        # TODO: Fill in gvars, lvars as env.Subst() does..
        if 'TARGET' not in lvars:
            d = create_subst_target_source_dict(target, source)
            if d:
                lvars = lvars.copy()
                lvars.update(d)

        retval = [[]]
        retval_index = 0

        if is_String(listSubstVal) and not isinstance(listSubstVal, CmdStringHolder):
            parts = listSubstVal.split()
            # This will yield a list(of tokens/args) of lists (of parts of a token/args)
            list_subst_list = [separate_args.findall(p) for p in parts]

            # listSubstVal = separate_args.findall(str(listSubstVal))  # In case it's a UserString.

            # Drop white space from splits. We'll be (likely) joining the elements with white space
            # and/or providing directly as arguments to popen().
            # listSubstVal = [i for i in listSubstVal if i[0] not in ' \t\r\f\v']
            # listSubstVal = [i for i in listSubstVal if not i[0].isspace()]

            try:
                debug("subst_list:IsString:%s", listSubstVal)
            except TypeError as e:
                debug("LKDJFKLSDJF")
        else:
            debug("subst_list:NotString:%r", listSubstVal)
            # This will yield a list(of tokens/args) of lists (of parts of a token/args)
            # Also need to handle when the list contains numbers which can't be regex'd
            list_subst_list = [isinstance(p, Number) and [p] or separate_args.findall(p) for p in listSubstVal]


        # At this point we should have a list where each element is a string representing a single argument
        # Each element will be a list generated by separate_args.findall() above.

        for element in list_subst_list:
            # Now process each argument

            # Elements should always be a list
            token_parts = []

            # If not then make a list
            if is_String(element):
                element = [element, ]

            for e in element:
                if isinstance(e, Number):
                    token_parts.append((str(e), ValueTypes.STRING))
                    # retval[retval_index].append(str(e))
                    continue

                if '\n' in e:
                    # Detected new line, add new element to retval as empty list.
                    retval_index += 1
                    retval.append([])

                if e.isspace():
                    token_parts.append((e, ValueTypes.STRING))
                    # retval[retval_index].append(e)
                    continue

                if '$' not in e:
                    token_parts.append((e, ValueTypes.STRING))
                    # retval[retval_index].append(e)
                    continue


                # returning a list
                this_value = EnvironmentValues.subst(e, env, mode=SubstModes.SUBST_LIST,
                                                     target=target, source=source,
                                                     gvars=gvars, lvars=lvars, conv=conv)
                print("Post_subst:%s"%this_value)
                # (List of (value,type) tuples)
                token_parts.extend(this_value)

            # TODO: Now we're getting back a list of string values, we need to re-build the string/lines and do the
            #  right thing with string escaping
            print("SUBST_LIST_TUPLE:(%s) -> (%s)" % (element, token_parts))

            # this_value = "".join([s for (s, t) in token_parts])
            # this_value = [s for (s, t) in token_parts]

            # TODO: Current implementation drops white space. Change logic and tests to expect it to be sanely preserved
            # this_value = [s for s in this_value if s and not s.isspace()]
            this_value = [(s, t) for (s, t) in token_parts if t != ValueTypes.WHITESPACE]

            # TODO: Implement splitting into multiple commands if there's a NEWLINE in any element.
            # for a in args:
            #     if a[0] in ' \t\n\r\f\v':
            #         if '\n' in a:
            #             self.next_line()
            #         elif within_list:
            #             self.append(a)
            #         else:
            #             self.next_word()
            #     else:
            #         self.expand(a, lvars, within_list)
            # TODO: Properly handle escaping $( $) which can cross recursive evaluation.
            #  Currently causing infinite recursion

            print("SUBST_LIST:(%s) -> (%s)" % (element, this_value))

            # TODO: IS this right Drop empty args?
            if not this_value:
                continue

            # Flatten this_value so it's a single level list
            # this_value = flatten(this_value)

            # add_value = "".join(this_value)

            retval[retval_index].append(this_value)
            # Now we need to determine if we need to recurse/evaluate this_value
            if False:
                if '$' not in this_value:
                    # no more evaluation needed
                    args = [a for a in separate_args.findall(this_value) if not a.isspace()]

                    retval[retval_index].extend(args)
                else:
                    # Need to handle multiple levels of recursion, also it's possible
                    # that escaping could span several levels of recursion so $( at top , and $)
                    # several levels lower. (This would be unwise.. do we need to enable this)
                    this_value_2 = EnvironmentValues.subst_list(this_value, env, mode, target, source, gvars, lvars,
                                                                conv)

                    debug("need to recurse")
                    raise Exception("need to recurse in subst_list: [%s]->{%s}" % (this_value, this_value_2))

        # debug("subst_list:%s", retval)

        # Now handle subst modes (includes escaping).
        retval = EnvironmentValues.process_subst_modes(retval, mode)

        # At this point w
        # new_retval = []
        # for line_no, line in enumerate(retval):
        #     new_retval.append([])
        #     for item in line:
        #         new_retval[line_no].append("".join(flatten([s for (s, t) in item])))

        return retval
