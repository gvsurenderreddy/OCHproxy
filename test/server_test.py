import os
import threading
import time
import pytest
import requests
from modules.Server import Server

@pytest.mark.timeout(20)
def test_server():
    thread = threading.Thread(target=run, args=())
    thread.start()
    time.sleep(2)
    r = requests.get("http://localhost:8182/")
    assert r.status_code == 200
    assert len(r.text) > 1


def run():
    Server(test=True, port=8182)
