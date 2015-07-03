import hashlib
import os
import tempfile
import pytest
from modules import Config

def setup_module(module):
    Config.CONFIG_PATH = tempfile.gettempdir() + "/ochproxy_test.json"

def test_none():
    with pytest.raises(TypeError):
        Config.Config.get(None)

def test_unset():
    assert Config.Config.get("q/q") is None

def test_path():
    json = '{"test": {"path": true}}'
    with open(Config.CONFIG_PATH, "w") as f:
        f.write(json)
    assert Config.Config.get("test/path") is True

def test_getall():
    Config.Config.get_all()

def test_set():
    Config.Config.set("q/w/e", True)
    assert Config.Config.get("q/w/e") is True

def test_save():
    with open(Config.CONFIG_PATH, "r") as f:
        x = hashlib.sha1(f.read().encode('utf-8'))
    Config.Config.set("foo/var", "raw")
    with open(Config.CONFIG_PATH, "r") as f:
        y = hashlib.sha1(f.read().encode('utf-8'))
    assert x != y

def teardown_module(module):
    os.remove(Config.CONFIG_PATH)
