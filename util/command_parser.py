from types import FunctionType


class Command:
    def __init__(self,
                 cmd_str: str = None,
                 sep: str = ' ',
                 control_characters: str = '"＂“”',
                 escape_func: tuple[FunctionType, FunctionType] = None,
                 max_len: int = 256,
                 cmd_header: str = '/'):
        """

        :param sep: Separator between parameters.
        :param escape_func: Tuple of escape and unescape functions, nullable.
        """
        self.control_characters = control_characters
        self.cmd_header = cmd_header
        self.max_len = max_len

        self.escape_func, self.unescape_func = escape_func if escape_func is not None else (None, None)
        self.sep = sep
        self.cmd_list = []
        if cmd_str is not None:
            if not self.load(cmd_str):
                raise ValueError()

    def load(self, cmd_str: str) -> bool:
        """

        :param cmd_str:
        :return:
        """
        i = 0
        in_ctrl = False
        cmd_str_p = ''
        for i in cmd_str:
            if i in self.control_characters:
                in_ctrl = not in_ctrl
            if in_ctrl:
                if i == ' ':
                    cmd_str_p += '/_'
                elif i == '/':
                    cmd_str_p += '//'
                else:
                    if i not in self.control_characters:
                        cmd_str_p += i
            else:
                if i not in self.control_characters:
                    cmd_str_p += i

        match_list = list(filter(lambda x: cmd_str.startswith(x), cmd_str_p))
        if len(match_list) > 0:
            prefix_len = max([len(i) for i in match_list])
        else:
            return False
        cmd_list = cmd_str_p[prefix_len:].split(self.sep, self.max_len)
        cmd_list = list(map(lambda x: x.replace('//', '/').replace('/_', ' '), cmd_list))
        self.cmd_list = ([self.unescape_func(i) for i in cmd_list]) if (self.unescape_func is not None) else cmd_list
        return True

    def pop(self, __index=0) -> str:
        if len(self.cmd_list) > 0:
            return self.cmd_list.pop(__index=__index)
        else:
            return ''

    def __getitem__(self, item):
        return self.cmd_list.__getitem__(item)

    def __setitem__(self, key, value):
        return self.cmd_list.__setitem__(key, value)

    def __delitem__(self, key):
        return self.cmd_list.__delitem__(key)

    def __len__(self):
        return self.cmd_list.__len__()

    def __iter__(self):
        return self.cmd_list.__iter__()

    def __reversed__(self):
        return self.__reversed__()

    def __contains__(self, item):
        return self.__contains__(item)

    def __str__(self):
        return self.sep.join(self.cmd_list)


if __name__ == '__main__':
    cmd = Command('/eee "55 5"')
    print(cmd)
