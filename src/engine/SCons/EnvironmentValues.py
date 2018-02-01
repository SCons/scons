import re
from SCons.Util import is_String, is_Sequence, CLVar
from SCons.Subst import CmdStringHolder, create_subst_target_source_dict, AllowableExceptions, raise_exception
from SCons.EnvironmentValue import EnvironmentValue, ValueTypes, separate_args, SubstModes


# _is_valid_var = re.compile(r'[_a-zA-Z]\w*$')
#
# _rm = re.compile(r'\$[()]')
# _remove = re.compile(r'\$\([^\$]*(\$[^\)][^\$]*)*\$\)')

_debug = True
if _debug:
    def debug(a):
        print(a)
else:
    def debug(a):
        pass


class EnvironmentValues(object):
    """
    A class to hold all the environment variables
    """
    def __init__(self, **kw):
        self.values = {}
        self._dict = {}
        for k in kw:
            self.values[k] = EnvironmentValue(kw[k])
            self._dict[k] = kw[k]
        self.key_set = set(self.values.keys())

    def __setitem__(self, key, value):
        debug("SETITEM:[%s]%s->%s"%(id(self),key,value))
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
        :return:
        """

        # Find all variables which depend on the key

        to_update = set([v for v in self.values if key in self.values[v].depends_on])

        # then recursively find all the other EnvironmentValue depending on
        # any keys which depend on the EnvironmentValue which depend on the key

        new_values_to_update = len(to_update)
        count = 0

        while new_values_to_update:
            new_values_to_update = False

            # Create a list of all values which need to be update by our current list
            # of to_update variables. This should recursively give us a list of
            # all variables invalidated by the key being changed.
            next_recursion_to_update = set([value for value in self.values
                                            for update_value in to_update
                                            if value not in update_value and
                                               update_value in self.values[value].depends_on])

            new_values_to_update = len(next_recursion_to_update) > 0
            if new_values_to_update:
                to_update.update(next_recursion_to_update)

            debug("Pass [%6d]"%count)
            count +=1

        for v in to_update:
            self.values[v].update(key, self.values)

    @staticmethod
    def subst(item, env, mode=0, target=None, source=None, gvars={}, lvars={}, conv=None):
        """
        Recursively Expand string
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

        if not gvars:
            gvars = env._dict

        if 'TARGET' not in lvars:
            d = create_subst_target_source_dict(target, source)
            if d:
                lvars = lvars.copy()
                lvars.update(d)

        try:
            if env.values[item].var_type == ValueTypes.STRING:
                return env.values[item].value
            elif env.values[item].var_type == ValueTypes.PARSED:
                return env.values[item].subst(env, mode=mode, target=target, source=source, gvars=gvars,
                                              lvars=lvars, conv=conv)
            elif env.values[item].var_type == ValueTypes.CALLABLE:
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
                # TODO: This can return a non-plain-string result which needs to be further processed.
                retval = env.values[item].value(target, source, env, (mode == SubstModes.FOR_SIGNATURE))
                return retval
        except KeyError as e:
            if is_String(item):
                # The value requested to be substituted doesn't exist in the EnvironmentVariables.
                # So, let's create a new value?
                # Currently we're naming it the same as it's content.
                # TODO: Should we keep these separate from the variables? We're caching both..
                env.values[item] = EnvironmentValue(item)
                return env.values[item].subst(env, mode=mode, target=target, source=source, gvars=gvars,
                                              lvars=lvars, conv=conv)
            elif is_Sequence(item):
                retseq = []
                for v in item:
                    val = EnvironmentValue(v)
                    retseq.append(val.subst(env, mode=mode, target=target, source=source, gvars=gvars,
                                            lvars=lvars, conv=conv))
                return retseq

    @staticmethod
    def subst_list(listSubstVal, env, mode=SubstModes.RAW,
                   target=None, source=None, gvars={}, lvars={}, conv=None):
        """Substitute construction variables in a string (or list or other
        object) and separate the arguments into a command list.

        The companion subst() function (above) handles basic substitutions within strings, so see
        that function instead if that's what you're looking for.

        :param listSubstVal: Either a string (potentially with embedded newlines),
                     or a list of command line arguments
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
        for_signature = mode == SubstModes.FOR_SIGNATURE

        # TODO: Fill in gvars, lvars as env.Subst() does..
        if 'TARGET' not in lvars:
            d = create_subst_target_source_dict(target, source)
            if d:
                lvars = lvars.copy()
                lvars.update(d)

        retval = [[]]
        retval_index = 0

        if is_String(listSubstVal) and not isinstance(listSubstVal, CmdStringHolder):
            listSubstVal = str(listSubstVal)  # In case it's a UserString.
            listSubstVal = separate_args.findall(listSubstVal)

            # Drop white space from splits. We'll be (likely) joining the elements with white space
            # and/or providing directly as arguments to popen().
            listSubstVal = [i for i in listSubstVal if i[0] not in ' \t\r\f\v']

            try:
                debug("subst_list:IsString:%s" % listSubstVal)
            except TypeError as e:
                debug("LKDJFKLSDJF")
        else:
            debug("subst_list:NotString:%s" % repr(listSubstVal))

        for element in listSubstVal:
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
            if '\n' in element:
                retval_index += 1
                retval.append([])

            e_value = EnvironmentValue(element, element)
            this_value = e_value.subst(env, mode=mode,
                                       target=target, source=source,
                                       gvars=gvars, lvars=lvars, conv=conv)

            args = [a for a in separate_args.findall(this_value) if a not in ' \t\r\f\v']

            # Now we need to determine if we need to recurse/evaluate this_value
            if '$' not in this_value:
                # no more evaluation needed
                retval[retval_index].extend(args)
            else:
                # Need to handle multiple levels of recursion, also it's possible
                # that escaping could span several levels of recursion so $( at top , and $)
                # several levels lower. (This would be unwise.. do we need to enable this)
                this_value_2 = EnvironmentValues.subst_list(this_value, env, mode, target, source, gvars, lvars, conv)

                debug("need to recurse")
                raise Exception("need to recurse in subst_list: [%s]->{%s}"%(this_value, this_value_2))

        debug("subst_list:%s" % [x for x in retval[retval_index]])

        return retval
