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
    time.sleep(4)
    r = requests.get("http://localhost:81/")
    assert r.status_code == 200
    assert len(r.text) > 1


def run():
    Server(test=True)
