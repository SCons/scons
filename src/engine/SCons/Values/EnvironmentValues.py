import re
from numbers import Number

import SCons.Environment
from SCons.Subst import create_subst_target_source_dict
from SCons.Util import is_String, is_Sequence
from SCons.Values import AllowableExceptions
from SCons.Values.CmdStringHolder import CmdStringHolder
from SCons.Values.EnvironmentValue import EnvironmentValue, ValueTypes, separate_args, SubstModes
# TODO: allow updating similar to Subst.SetAllowableExceptions()
from SCons.Values.ListSubstWorker import ListWorker
from SCons.Values.ParsedEnvironmentValue import ParsedEnvironmentValue
from SCons.Values.StringSubstWorker import StringSubstWorker

# import pysnooper
# AllowableExceptions = (IndexError, NameError)

# _is_valid_var = re.compile(r'[_a-zA-Z]\w*$')
#
# _rm = re.compile(r'\$[()]')
# _remove = re.compile(r'\$\([^\$]*(\$[^\)][^\$]*)*\$\)')

# This regular expression is used to replace strings of multiple white
# space characters in the string result from the scons_subst() function.
space_sep = re.compile(r'[\t ]+(?![^{]*})')

_debug = True
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


class EnvironmentValues(object):
    """
    A class to hold all the environment variables
    """
    __slots__ = ['values', '_dict', 'key_set', 'cached_values']

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

            # Create a list of all values which need to be updated by our current list
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
            if count > 1000:
                # TODO Why?
                raise Exception("in update_cached_values key:%s count>1000 [%d]"%(key,count))

        for k in to_update:
            self.values[k].update(key, self.values)

    def resolve_unassigned_types(self, substWorker, gvars, lvars):
        """
        Use the context to remove uncertainty on types
        :param substWorker: Either ListSubstWorker or StringSubstWorker object
        :param gvars:
        :param lvars:
        :return:
        """

        # Now we should be able to resolve if value is a callable or a variable.
        # if unsure, we'll leave as callable.
        for i,pv in enumerate(substWorker.parsed_values):
            if pv is None:
                continue
            rv = pv.resolve_unassigned_types(self, gvars)
            if rv == 2:
                # It's ok to have an undefined variable. Just replace with blank.
                substWorker.string_values[i] = ''
                substWorker.parsed_values[i] = None

        debug("==============================")
        debug("After resolving unknown types:")
        EnvironmentValue.debug_print_parsed_parts(substWorker.parsed_values)

    # @pysnooper.snoop()
    def evaluate_parsed_values(self, subst_worker, global_vars, local_vars, mode, conv=None):
        """
        Walk the list of parsed values and evaluate each in turn.  Possible return values for each are:
        * A plain string (No $ values)
        * A non-plain string (requires parsing and evaluation)
        * A collection of values (all plain strings)
        * A collection of values (not ALL plain strings)
        * Callable object

        :param subst_worker: A StringSubstWorker or ListSubstWorker object
        :param global_vars:
        :param local_vars:
        :param mode:
        :param conv: function to convert results for return (typically str to get a string from whatever object)
        :return:
        """

        for_signature = mode == SubstModes.FOR_SIGNATURE

        for index, pv in enumerate(subst_worker.parsed_values[:]):

            # In the case there are any values in string_values, and any parsed_values are None
            # ensure we are not losing the existing string_values.
            if pv is None:
                subst_worker.new_parsed_values.append(None)
                subst_worker.new_string_values.append(subst_worker.string_values[index])
                continue

            # Now handle all the various types which can be in the value.
            if pv.type == ValueTypes.STRING:
                # should yield a single value

                # The variable resolved to a string . No need to process further.
                debug("STR      %s" % pv)
                subst_worker.new_string_values.append((pv.value, pv.type))
                subst_worker.new_parsed_values.append(None)
                debug("%s->%s" % (pv.value, subst_worker.string_values[pv.position]))

            elif pv.type == ValueTypes.PARSED:
                # Can be multiple values
                debug("PARSED   %s" % pv)

                try:
                    # Now get an EnvironmentValue object to continue processing.
                    try:
                        value = EnvironmentValue.factory(pv.lvars[pv.value])
                    except KeyError as e:
                        value = self.values[pv.value]

                    # Now use value.var_type to decide how to proceed.
                    if value.var_type == ValueTypes.NUMBER:
                        subst_worker.new_string_values.append((value, ValueTypes.NUMBER))
                        subst_worker.new_parsed_values.append(None)

                    elif value.var_type == ValueTypes.STRING:
                        self_ref_location = value.value.find(pv.value)
                        if self_ref_location != -1 and value.value[self_ref_location - 1] == '$':
                            #
                            pass

                        if len(value.value) > 1 and value.value[0] == '$' and value.value[1:] == pv.value:
                            # Special case, variables value references itself and only itself
                            subst_worker.new_string_values.append(('', ValueTypes.STRING))
                            subst_worker.new_parsed_values.append(None)
                        else:
                            subst_worker.new_string_values.append((value.value, ValueTypes.STRING))
                            subst_worker.new_parsed_values.append(None)
                    # elif value.var_type == ValueTypes.PARSED and value.value[0] == '$' and value.value[1:] == pv.value:
                    #     # TODO: need to check if any of the parts of this string have $ and match the current value
                    #     #  name so value.value = 'a $NAME b' where pv.value=='NAME'
                    #
                    #     # Handle when the value of the current value is a self reference 'R'='$R'.
                    #     # This prevents infinite recursion during evaluation and mimics previous
                    #     # functionality
                    #     new_string_values.append(('', ValueTypes.STRING))
                    #     new_parsed_values.append(None)
                    elif value.var_type == ValueTypes.COLLECTION:
                        # We may have received multiple values which may need further expansion.
                        # TODO: Not sure this is correct/best way.
                        #  Do we need to maintain groups of collections for building command line - YES.
                        npv = []
                        nsv = []
                        for (t, v, i) in value.all_dependencies:
                            pv.lvars = pv.lvars.copy()
                            pv.lvars[pv.value] = ''

                            if v == pv.value:
                                npv.append(None)
                                nsv.append(('', ValueTypes.STRING))
                            else:
                                npv.append(ParsedEnvironmentValue(t, v, i, pv.lvars))
                                nsv.append(None)

                        subst_worker.new_parsed_values.extend(npv)
                        subst_worker.new_string_values.extend(nsv)
                    else:
                        npv = []
                        nsv = []
                        for (t, v, i) in value.all_dependencies:
                            # blank out value in propagated lvars to prevent recursive variable loops
                            pv.lvars = pv.lvars.copy()
                            pv.lvars[pv.value] = ''

                            if v == pv.value:
                                npv.append(None)
                                nsv.append(('', ValueTypes.STRING))
                            else:
                                npv.append(ParsedEnvironmentValue(t, v, i, pv.lvars))
                                nsv.append(None)

                        subst_worker.new_parsed_values.extend(npv)
                        subst_worker.new_string_values.extend(nsv)

                    debug("%s->%s" % (pv.value, subst_worker.string_values[pv.position]))
                except KeyError as e:
                    if KeyError in AllowableExceptions:
                        subst_worker.new_string_values.append(('', ValueTypes.STRING))
                        subst_worker.new_parsed_values.append(None)

            elif pv.type == ValueTypes.CALLABLE:
                # Can return multiple values
                # TODO: What should V be. If it's a function it seems the name ends up in v, but if callable class
                #    v ends up being an instance of the callable class.  Both of which can return another callable
                #    or a string which requires further processing, or a plain string, or blank.
                if pv.value in self.values:
                    to_call = self.values[pv.value].value
                elif pv.value in local_vars:
                    to_call = pv.lvars[pv.value]
                else:
                    print("Couldn't find key :%s" % pv.value)
                    to_call = pv.value

                call_value = self.eval_callable(to_call, subst_worker.parsed_values, subst_worker.string_values,
                                                target=local_vars['TARGETS'],
                                                source=local_vars['SOURCES'],
                                                global_vars=global_vars, local_vars=local_vars, mode=mode,
                                                conv=conv)

                new_values = []
                if is_String(call_value):
                    if '$' not in call_value:
                        subst_worker.new_string_values.append((call_value, ValueTypes.STRING))
                        subst_worker.new_parsed_values.append(None)

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
                        subst_worker.new_string_values.append((val, ValueTypes.NUMBER))
                        subst_worker.new_parsed_values.append(None)

                    elif val.var_type == ValueTypes.STRING:
                        if val[0] == '$' and val[1:] == pv.value:
                            # Special case, variables value references itself and only itself
                            subst_worker.new_string_values.append(('', ValueTypes.STRING))
                            subst_worker.new_parsed_values.append(None)

                        else:
                            subst_worker.new_string_values.append((val.value, ValueTypes.STRING))
                            subst_worker.new_parsed_values.append(None)

                    else:
                        # TODO: Handle other recursive loops by empty stringing this value before recursing with copy of lvar?
                        subst_worker.new_parsed_values.extend(val.all_dependencies)
                        subst_worker.new_string_values.extend([None] * len(val.all_dependencies))

                # # TODO: Handle return value not being a string, (a collection for example)
                #

            elif pv.type == ValueTypes.NUMBER:
                # yields single value

                # The variable resolved to a number. No need to process further.
                debug("Num      %s" % pv)
                debug("%s->%s" % (pv.value, (str(self[pv.value].value), t)))
                subst_worker.new_string_values.append(str(self[pv.value].value), t)
                subst_worker.new_parsed_values.append(None)

            elif pv.type == ValueTypes.COLLECTION:
                # Note: each item in the collection creates a new argument at the end of it
                # so if the argument thus far is 'a', and the collection is ['B','C','D']
                # We should end up with a string like this: 'aB C D'
                # or if we're dealing with subst_list: 'aB','C','D' - we cannot do this by add ' ' as our arguments
                # can have embedded whitespace now.
                # TODO:  How many values?

                # Handle list, tuple, or dictionary
                # Basically iterate all items, evaluating each, and then join them together with a space
                debug("COLLECTION  %s" % pv)
                value = self[pv.value].value

                # TODO: Finish implementation
                # This is very simple implementation which ignores nested collections and values which
                # need to be further evaluated.(subst'd)

                subst_worker.new_string_values.append((" ".join(value), t))
                subst_worker.new_parsed_values.append(None)

            elif pv.type in (ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                # Can yield multiple values

                try:
                    # Note: this may return a callable or a string or a number or an object.
                    # If it's callable, then it needs be executed by the logic above for ValueTypes.CALLABLE.
                    # TODO Fix gvars to have contents of variables rather than evaluating to EnvironmentValue object...
                    sval = eval(pv.value, global_vars, local_vars)
                except AllowableExceptions as e:
                    sval = ''

                if is_String(sval):
                    subst_worker.new_string_values.append((sval, ValueTypes.NUMBER))
                    subst_worker.new_parsed_values.append(None)

                elif callable(sval):
                    subst_worker.new_parsed_values.append((ValueTypes.CALLABLE, sval, i))
                    subst_worker.new_string_values.append(None)

            elif pv.type == ValueTypes.VARIABLE_OR_CALLABLE and pv.value not in pv.lvars and pv.value not in global_vars:
                # Handle when variable is NOT defined by having blank string
                subst_worker.new_string_values.append(('', ValueTypes.STRING))
                subst_worker.new_parsed_values.append(None)

            elif pv.type in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                # Propagate escapes into string_values. Escaping is not done here.
                subst_worker.new_string_values.append((pv.value, pv.type))
                subst_worker.new_parsed_values.append(None)

            else:
                # SHOULD NEVER GET HERE. Drop into debugger if so.
                debug("AAHAHAHHAH BROKEN")
                # import pdb; pdb.set_trace()

        # Now correct index # for each item in new_parsed_values
        for (i, pv) in enumerate(subst_worker.new_parsed_values):
            if pv is not None:
                pv.position = i

        parsed_values = [pv is not None and pv or None for (i, pv) in enumerate(subst_worker.new_parsed_values)]
        string_values = subst_worker.new_string_values
        return parsed_values, string_values

    def eval_callable(self, to_call, subst_worker,
                      target=None, source=None, global_vars={}, local_vars={}, mode=SubstModes.RAW, conv=None):
        """
        Evaluate a callable and return the generated string.
        (Note we'll need to handle recursive expansion)
        :param to_call: The callable to call..
        :param subst_worker: StringSubstWorker or ListSubstWorker object.
        :param global_vars:
        :param local_vars:
        :return:
        """

        if 'TARGET' not in local_vars:
            d = self.create_local_var_dict(target, source)
            if d:
                local_vars = local_vars.copy()
                local_vars.update(d)

        try:
            s = to_call(target=local_vars['TARGETS'],
                        source=local_vars['SOURCES'],
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
    def subst(subst_string, env, mode=0, target=None, source=None, global_vars={}, local_vars={}, conv=None):
        """
        Recursively Expand string
        :param subst_string: The string to be expanded.
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
        :param global_vars: Specify the global variables. Defaults to empty dict, which will yield using this EnvironmentValues
                      symbols.
        :param local_vars: Specify local variables to evaluation the variable with. Usually this is provided by executor.
        :return: expanded string
        """
        # subst called with plain string, just return it.
        if '$' not in subst_string:
            if mode != SubstModes.SUBST_LIST:
                return subst_string
            else:
                return [(subst_string, ValueTypes.STRING)]

        # TODO: Case to shortcut.  subst_string = "$VAR" and env['VAR'] = simple string.
        #  This happens enough to make it worth optimizing
        # if ' ' not in subst_string and subst_string[0]=='$' and

        # TODO:Figure out how to handle this properly.  May involve seeing if source & targets is specified. Or checking
        #      against list of variables which are "ok" to leave undefined and unexpanded in the returned string and/or
        #      the cached values.  This is likely important for caching CCCOM where the TARGET/SOURCES will change
        #      and there is still much value in caching whatever else can be cached from such strings
        ignore_undefined = False

        use_cache_item = 0
        if mode == SubstModes.FOR_SIGNATURE:
            use_cache_item = 1

        if not global_vars:
            global_vars = env._dict

        overrides = set()
        if local_vars:
            # keys in lvars is going to be overrides
            overrides = overrides.union(local_vars.keys())

            # remove reserved vars from the list
            overrides -= SCons.Environment.reserved_construction_var_names_set

        if 'TARGET' not in local_vars:
            d = create_subst_target_source_dict(target, source)
            if d:
                local_vars = local_vars.copy()
                local_vars.update(d)

        # Stick the element in a list, evaluate all elements in list until empty/all evaluated.
        # If evaluation returns a list from a single element insert that new list at the point the element
        # being evaluated was previously at.

        try:
            # First retrieve the value by subst_string and the applicable overrides.
            # TODO: Transpose overrides set into something which is cache-able. String for now, but maybe tuple instead?
            override_string = "-".join(sorted(overrides))

            val = env.cached_values[(subst_string, override_string)]
        except KeyError as e:
            # No such value create one
            val = EnvironmentValue.factory(subst_string)

        working_object = StringSubstWorker(val, mode, local_vars, global_vars, conv)

        working_object.split_dependencies(SCons.Environment.reserved_construction_var_names_set)

        working_object.resolve_parsed_values(env)

        # Now handle subst mode during string expansion.
        if mode == SubstModes.SUBST_LIST:
            return working_object.string_values
        elif mode == SubstModes.FOR_SIGNATURE:
            string_values = remove_escaped_items_from_list(working_object.string_values)
        elif mode == SubstModes.NORMAL:
            string_values = [(s, t) for (s, t) in working_object.string_values if s not in ('$(', '$)')]
        # else Remaining mode is RAW where we don't strip anything.

        retval = " ".join([s for s, t in working_object.string_values])

        if mode in (SubstModes.FOR_SIGNATURE, SubstModes.NORMAL):
            retval = space_sep.sub(' ', retval).strip()

        return retval

    @staticmethod
    def subst_list(list_subst_value, env, mode=SubstModes.RAW,
                   target=None, source=None, global_vars={}, local_vars={}, conv=None):
        """Substitute construction variables in a string (or list or other
        object) and separate the arguments into a command list.

        The companion subst() function (above) handles basic substitutions within strings, so see
        that function instead if that's what you're looking for.

        :param list_subst_value: Either a string (potentially with embedded newlines),
                     or a list of command line arguments.
        :param env:
        :param mode:
        :param target:
        :param source:
        :param global_vars:
        :param local_vars:
        :param conv:
        :return:  a list of lists of substituted values (First dimension is separate command line,
                  second dimension is "words" in the command line)

        """
        # TODO: Fill in global_vars, local_vars as env.Subst() does..
        if 'TARGET' not in local_vars:
            d = create_subst_target_source_dict(target, source)
            if d:
                local_vars = local_vars.copy()
                local_vars.update(d)

        retval = ListWorker(list_subst_value)

        if is_String(list_subst_value) and not isinstance(list_subst_value, CmdStringHolder):
            parts = list_subst_value.split()
            # This will yield a list(of tokens/args) of lists (of parts of a token/args)
            list_subst_list = [separate_args.findall(p) for p in parts]

            # listSubstVal = separate_args.findall(str(listSubstVal))  # In case it's a UserString.

            # Drop white space from splits. We'll be (likely) joining the elements with white space
            # and/or providing directly as arguments to popen().
            # listSubstVal = [i for i in listSubstVal if i[0] not in ' \t\r\f\v']
            # listSubstVal = [i for i in listSubstVal if not i[0].isspace()]

            try:
                debug("subst_list:IsString:%s [%s]", list_subst_value, list_subst_list)
            except TypeError as e:
                debug("subst_list.. should never get here")
        else:
            debug("subst_list:NotString:%r", list_subst_value)
            # This will yield a list(of tokens/args) of lists (of parts of a token/args)
            # Also need to handle when the list contains numbers which can't be regex'd
            list_subst_list = [isinstance(p, Number) and [p] or separate_args.findall(p) for p in list_subst_value]

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
                    continue

                if '\n' in e:
                    # Detected new line, add new element to return_value as empty list.
                    retval_index += 1
                    retval.append([])

                if e.isspace():
                    token_parts.append((e, ValueTypes.STRING))
                    continue

                if '$' not in e:
                    token_parts.append((e, ValueTypes.STRING))
                    continue

                # We assume returning a list which represents a single argument
                # However, the issue with this, we assume we're processing a single argument, but when whatever
                # this value is contains a list (which are each a separate argument), then we end up doing
                # the wrong thing To fix this, I think we need to pass an object into this logic which
                # knows how to add token parts and arguments properly..?
                this_value = EnvironmentValues.subst(e, env, mode=SubstModes.SUBST_LIST,
                                                     target=target, source=source,
                                                     global_vars=global_vars, local_vars=local_vars, conv=conv)
                print("Post_subst:%s" % this_value)
                # (List of (value,type) tuples)
                token_parts.extend(this_value)

            # TODO: Now we're getting back a list of string values, we need to re-build the string/lines and do the
            #  right thing with string escaping
            print("SUBST_LIST_TUPLE:(%s) -> (%s)" % (element, token_parts))

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

            # return_value[retval_index].append(this_value)
            retval.current_value = this_value
            retval.new_argument()

        # debug("subst_list:%s", return_value)

        # Now handle subst modes (includes escaping).
        retval.process_subst_modes(mode)

        return retval.retval
