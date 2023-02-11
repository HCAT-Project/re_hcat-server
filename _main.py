import json
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


def load_config(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(path)


def main():
    from server import Server
    arg = get_start_arg({'debug': False, 'config': 'config.json'})

    config_path = arg['config']
    config = load_config(config_path)
    s = Server(debug=arg['debug'])
    s.start()
