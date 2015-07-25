from urllib2 import URLError
import pytest
from modules.Request import Request


def test_invalid_url():
    r = Request(url="http://example.example/example", payload={"foo": "bar"})
    with pytest.raises(URLError):
        r.open()
    with pytest.raises(URLError):
        r.send()

def test_user_agent():
    r = Request(url="http://httpbin.org/user-agent").send()
    j = r.json
    assert "user-agent" in j
    assert len(j["user-agent"]) > 1
    assert "Python" not in j["user-agent"]

def test_cookies():
    Request(url="http://httpbin.org/cookies/set?k1=v1").send()
    r = Request(url="http://httpbin.org/cookies").send().json
    assert "cookies" in r
    assert "k1" in r["cookies"]
    assert r["cookies"]["k1"] == "v1"

def test_post():
    r = Request()
    r.set_payload({"hello": "httpbin!"})
    r.set_method("POST")
    r.set_url("http://httpbin.org/post")
    r = r.send().json
    assert "form" in r
    assert r["form"]["hello"] == "httpbin!"
