import json
from modules import Request
from modules.BasePlugin import *
from modules.Config import Config


class DebridItalia(BasePlugin):
    priority = Priority.MULTI_UNLIMITED
    config_values = ["user", "password"]

    def __init__(self):
        super(DebridItalia, self).__init__()
        # Debrid Italia only has a list of all hosts, no exact format for the links
        r = Request.Request(url="http://debriditalia.com/api.php?hosts").send().text
        r = "[" + r + "]"
        hosts = json.loads(r)
        for host in hosts:
            regex = "https?://(www\.)?" + host + ".*"
            DebridItalia.link_format.append(regex)

    @cache(10*60)
    def handle(self, link):
        r = Request.Request("http://www.debriditalia.com/api.php", payload={
            'generate': "on",
            'link': link,
            'p': Config.get("password"),
            'u': Config.get("user")}).send()
        if "ERROR:" not in r.text:
            return Request.Request(url=r.text.strip())
        # TODO: Error codes
        self.deactivate()
        raise Errors.PluginError
