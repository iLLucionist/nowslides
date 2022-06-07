from inspect import getmembers, isfunction
import yaml


class Cache(dict):
    _disable = False

    def __init__(self, action, disable=False):
        self.action = action
        self._disable = disable

    def __getitem__(self, key):
        if key not in self.keys():
            value = self.action(key)
            super().__setitem__(key, value)
        if self._disable is True:
            value = self.action(key)
            super().__setitem__(key, value)
        return super().__getitem__(key)


def load_yaml(fname):
    with open(fname, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)


def module_to_dict(module):
    return dict(getmembers(module, isfunction))

# module_to_dict = lambda module: dict( getmembers( module, isfunction ) )
