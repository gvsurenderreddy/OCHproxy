import hashlib
import os
import pytest
from modules.Config import Config


def test_none():
    with pytest.raises(TypeError):
        Config.get(None)

def test_unset():
    assert Config.get("q/q") is None

def test_path():
    json = '{"test": {"path": true}}'
    with open("config.json", "w") as f:
        f.write(json)
    assert Config.get("test/path") is True

def test_getall():
    Config.get_all()

def test_set():
    Config.set("q/w/e", True)
    assert Config.get("q/w/e") is True

def test_save():
    with open("config.json", "r") as f:
        x = hashlib.sha1(f.read())
    Config.set("foo/var", "raw")
    with open("config.json", "r") as f:
        y = hashlib.sha1(f.read())
    assert x != y

def teardown_module(module):
    os.remove("config.json")
