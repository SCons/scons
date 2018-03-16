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

        # Next take the dependencies and stick them in either string_values or parsed_values
        # parsed_values indicates they need further processing to be turned into plain strings

        # Break parts in to simple strings or parts to be further evaluated
        for (t, v, i) in self.all_dependencies:
            if t not in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END, ValueTypes.STRING) and v in env \
                    and env[v].is_cached(env):
                string_values[i] = (env[v].cached[use_cache_item], t)
            elif t in (ValueTypes.ESCAPE_START, ValueTypes.ESCAPE_END):
                string_values[i] = (v, t)
            elif t in (ValueTypes.VARIABLE, ValueTypes.EVALUABLE, ValueTypes.FUNCTION_CALL):
                parsed_values[i] = (t, v, i)
            elif t == ValueTypes.CALLABLE:
                # Put the actual value to be called in v, rather than the EnvironmentValue.
                try:
                    v = lvars[v]
                except KeyError as e:
                    v = env[v].value

                parsed_values[i] = (t, v, i)
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

                parsed_values[i] = (t, v, i)
            else:
                string_values[i] = (v, t)

        debug("Parsed values:%s  for %s [%s]", parsed_values, self._parsed, string_values)

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
                        nt = ValueTypes.PARSED  # Should we have lvars type?
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
                (t, v, i) = pv

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
                        debug("Swapped to EVALUABLE:%s", v)
                        t = ValueTypes.EVALUABLE

                # Now handle all the various types which can be in the value.
                if t == ValueTypes.CALLABLE:
                    to_call = v

                    call_value = self.eval_callable(to_call, parsed_values, string_values, target=target,
                                                    source=source, gvars=env, lvars=lvars, for_sig=for_signature)

                    # TODO: Handle return value not being a string, (a collection for example)

                    if is_String(call_value) and '$' not in call_value:
                        string_values[i] = (call_value, ValueTypes.STRING)
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
                            string_values[i] = (
                            ev.subst(env, mode, target, source, gvars, lvars, conv), ValueTypes.STRING)

                    parsed_values[i] = None
                elif t == ValueTypes.PARSED:
                    debug("PARSED   Type:%s VAL:%s", pv[0], pv[1])

                    try:
                        try:
                            value = lvars[v]
                        except KeyError as e:
                            value = env[v].value

                        # Shortcut self reference
                        if isinstance(value, Number):
                            string_values[i] = (value, ValueTypes.NUMBER)
                        elif is_String(value) and len(value) > 1 and value[0] == '$' and value[1:] == v:
                            # TODO: Is this worth doing? (Check line profiling once we get all functionality working)
                            # Special case, variables value references itself and only itself
                            string_values[i] = ('', ValueTypes.STRING)
                        else:
                            # TODO: Handle other recursive loops by empty stringing this value before recursing with copy of lvar?
                            string_values[i] = (env[v].subst(env, mode, target, source, gvars, lvars, conv),
                                                ValueTypes.STRING)
                        debug("%s->%s", v, string_values[i])
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
                    debug("STR      Type:%s VAL:%s", pv[0], pv[1])
                    string_values[i] = (env[v].value, t)
                    debug("%s->%s", v, string_values[i])
                    parsed_values[i] = None
                elif t == ValueTypes.NUMBER:
                    # The variable resolved to a number. No need to process further.
                    debug("Num      Type:%s VAL:%s", pv[0], pv[1])
                    string_values[i] = (str(env[v].value), t)
                    debug("%s->%s", v, string_values[i])
                    parsed_values[i] = None
                elif t == ValueTypes.COLLECTION:
                    # Handle list, tuple, or dictionary
                    # Basically iterate all items, evaluating each, and then join them together with a space
                    debug("COLLECTION  Type:%s VAL:%s", t, v)
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
                    string_values[i] = ('', ValueTypes.STRING)  # not defined so blank string
                    parsed_values[i] = None
                else:
                    debug("AAHAHAHHAH BROKEN")
                    import pdb;
                    pdb.set_trace()

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
                in_escape_count += 1
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

        debug("HERE:%s  Escaped:%s", subst_value, signature_string)

        # Cache both values
        self.cached = (subst_value, signature_string)

        if not for_signature:
            return subst_value
        else:
            return signature_string