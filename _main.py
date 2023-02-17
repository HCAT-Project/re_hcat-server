import json
import sys


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
            value = sys.argv[_i + 1]
            if i[1:] in init_list:
                value = type(init_list[i[1:]])(value)
            setattr(arg, i[1:], value)

    for i in sys.argv:
        if i.startswith('--'):
            setattr(arg, i[2:], True)
    return arg


def load_config(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def main():
    from server import Server
    arg = get_start_arg({'debug': False, 'config': 'config.json', 'host': '0.0.0.0', 'port': 8080})

    config_path = arg['config']
    config = load_config(config_path)
    s = Server(debug=arg['debug'], address=(arg['host'], arg['port']), config=config)
    s.start()
