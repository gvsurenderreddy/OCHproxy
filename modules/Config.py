import inspect
import json
import os
import re
import shutil

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'config.json'))


class Config(object):
    def __init__(self):
        pass

    __author__ = 'bauerj'
    config = None
    config_changed = 0

    @staticmethod
    def set(key, value):
        Config.traverse(key, set_to=value)

    @staticmethod
    def get(key, default=None):
        key = Config.qualify(key)
        (key, c) = Config.traverse(key, default)
        if key in c:
            return c[key]
        return default

    @staticmethod
    def get_all():
        try:
            if Config.config is None or Config.config_changed is not os.stat(CONFIG_PATH)[8]:
                with open(CONFIG_PATH) as config_file:
                    Config.config = json.load(config_file)
                    Config.config_changed = os.stat(CONFIG_PATH)[8]
            return Config.config
        except ValueError:
            print "ATTENTION: config.json did not contain valid json. The config file will be recreated"
            print "A backup of the current file can be found in config.json.invalid"
            shutil.copyfile(CONFIG_PATH, CONFIG_PATH + ".invalid")
        except (IOError, OSError):
            pass
        return {}

    @staticmethod
    def save(c):
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(c, config_file, indent=4)

    @staticmethod
    def traverse(key, default=None, set_to=None):
        full = c = Config.get_all()
        changed = False
        while "/" in key:
            index = key.split("/")[0]
            if index not in c:
                c[index] = {}
                changed = True
            c = c[index]
            key = "/".join(key.split("/")[1:])
        if key not in c:
            c[key] = default
            changed = True
        if set_to is not None:
            c[key] = set_to
            changed = True
        if changed:
            Config.save(full)
        return key, c

    @staticmethod
    def qualify(key):
        if "/" in key:
            return key
        try:
            stack = inspect.stack(0)
            caller_file = stack[2][1].rstrip(".py")
            qualifier = re.findall("\w+", caller_file)
            return "/".join(qualifier) + "/" + key
        except KeyError:
            return key
