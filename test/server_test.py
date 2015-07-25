import socket
import tempfile
import threading
import time
import pytest
from modules.Request import Request
from modules.Server import Server


@pytest.mark.timeout(20)
def test_server():
    start_server(8182)
    r = Request(url="http://localhost:8182/").send()
    assert r.status_code == 200
    assert len(r.text) > 1


@pytest.mark.timeout(20)
def test_auth():
    start_server(8183)
    r = Request(url="http://localhost:8183/get?link=123").send()
    assert r.status_code != 200

@pytest.mark.timeout(20)
def test_account():
    start_server(8184)
    r = Request(url="http://localhost:8184/account?user=admin&password=123123").send()
    assert r.status_code == 200

@pytest.mark.timeout(20)
def test_links():
    start_server(8185)
    r = Request(url="http://localhost:8185/links?user=admin&password=123123").send()
    assert r.status_code == 200


def start_server(port, execute=None):
    thread = threading.Thread(target=execute or run, kwargs={"port": port})
    thread.start()
    time.sleep(6)


def run(port=8182):
    from modules.Auth import Auth
    # mock users list
    Auth.user = {'admin': Auth.User('admin', '123123')}
    Auth.file_data = float('Inf')
    # mock Config
    from modules.Config import Config
    Config.CONFIG_PATH = tempfile.gettempdir() + "/ochproxy_test" + str(port) + ".json"
    Config.config_changed = float('Inf')
    Config.config = {'app': {'debug': True},
                     'hoster': {'TestPlugin': {'active': True}}
                     }
    Server(test=True, port=port)
