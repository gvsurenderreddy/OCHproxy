import json


class Config:
    def __init__(self):
        pass

    __author__ = 'bauerj'

    @staticmethod
    def set(key, value):
        (key, c) = Config.traverse(key)
        c[key] = value
        Config.save(c)

    @staticmethod
    def get(key, default=None):
        (key, c) = Config.traverse(key, default)
        if key in c:
            return c[key]
        return default

    @staticmethod
    def get_all():
        try:
            with open('config.json') as config_file:
                return json.load(config_file)
        except (ValueError, IOError):
            return {}

    @staticmethod
    def save(c):
        with open('config.json', 'w') as config_file:
            json.dump(c, config_file, indent=4)

    @staticmethod
    def traverse(key, default=None):
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
        if changed:
            Config.save(full)
        return key, c
