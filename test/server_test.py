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

def start_server(port):
    thread = threading.Thread(target=run, kwargs={"port": port})
    thread.start()
    time.sleep(1)

def run(port=8182):
    Server(test=True, port=port)
