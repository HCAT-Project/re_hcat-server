import sys
import logging


def get_start_arg(init_list):
    class Object:
        def __getitem__(self, item):
            return getattr(self, item)

    arg = Object()
    _vars = globals()

    for i in init_list:
        setattr(arg, i, init_list[i])

    for _i in range(len(sys.argv)):
        i = sys.argv[_i]
        if i.startswith('-') and not i.startswith('--'):
            setattr(arg, i[1:], sys.argv[_i + 1])

    for i in sys.argv:
        if i.startswith('--'):
            setattr(arg, i[2:], True)
    return arg


def main():
    from server import Server
    arg = get_start_arg({"debug": False})
    handler = logging.FileHandler('log.txt', encoding='utf8')
    logging.getLogger().addHandler(handler)
    s = Server(debug=arg['debug'])
    s.start()
