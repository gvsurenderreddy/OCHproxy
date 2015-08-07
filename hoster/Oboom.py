from modules.BasePlugin import *
from modules.Request import Request
from modules.Config import Config
from modules.Log import log
from pbkdf2 import PBKDF2


class Oboom(BasePlugin):
    hostname = "oboom.com"
    priority = Priority.DIRECT_UNLIMITED
    config_values = ["email", "password"]

    def __init__(self):
        super(Oboom, self).__init__()
        self.cookie = ""
        self.login()

    def login(self):
        pw = Config.get("password")
        salt = pw[::-1]
        # seems like they take security serious
        hash = PBKDF2(pw, salt, 10**3).hexread(16)

        r = Request("https://www.oboom.com/1/login", payload={
            'auth': Config.get("email"),
            'pass': hash
        })
        r.add_header("origin", "https://www.oboom.com")
        r.add_header("referer", "https://www.oboom.com/")
        r.add_header("x-requested-with", "XMLHttpRequest")
        r = r.send()
        if r.status_code is not 200:
            log.error("oboom.com Login failed: " + r.text)
            self.deactivate()
            return
        self.cookie = r.json[1]["session"]

    def handle(self, link):
        id = link.split(".com/", 1)[1]
        id = id.split("/", 1)[0]
        r = Request("http://api.oboom.com/1/dl", payload={
            "token": self.cookie,
            "item": id,
            "redirect": True
        })
        r = r.open_for_user()
        if r.getcode() in [404, 410]:
            raise Errors.InvalidLinkError(r.read())
        if r.getcode() is not 200:
            raise Errors.TemporarilyImpossibleError(r.read())
        return r
