from SCons.Values.EnvironmentValue import ValueTypes, SubstModes


class ListWorker(object):
    """
    This is used to hold the work in progress for subst_list
    """

    def __init__(self, list_subst_value):
        self.listSubstVal = list_subst_value

        # Array of lines made of an array of arguments
        self.retval = [[]]
        self.retval_index = 0
        self.current_value = []

    def add_token(self, token):
        self.current_value.append(token)

    def new_argument(self):
        argument = "".join(self.current_value)
        self.retval[self.retval_index].append(argument)
        self.current_value = []

    def new_line(self):
        self.retval.append([])
        self.retval_index += 1

    def process_subst_modes(self, mode):
        """
        Return escaped array of string results
        :param mode - SubstValue type (indicating what we should do with signature escapes $( and $)
        :return: escape processed array of strings
        """

        retval = []
        escape_level = 0
        for line_no, line in enumerate(self.retval):
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
                    # return_value[line_no].append("".join(word))
                    retval[line_no].extend(word)

                # if parts and len(parts) >= 1 and parts[0] != '':  # or mode == SubstModes.RAW:
                #     return_value[line_no].append("".join(parts))
                # else:
                #     pass
        self.retval = retval