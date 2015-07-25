import json
from modules import Request
from modules.BasePlugin import *
from modules.Config import Config
from modules.Log import log

class PremiumTo(BasePlugin):
    priority = Priority.MULTI_LIMITED
    config_values = ["user", "password"]

    def __init__(self):
        super(PremiumTo, self).__init__()
        r = Request.Request(url="http://api.premium.to/hosts.php").send().text
        PremiumTo.hostname = r.split(";")
        if not self.login():
            log.error("premium.to account data is invalid. Deactivating plugin.")
            self.deactivate()

    def login(self):
        r = Request.Request("http://premium.to/login.php", method="POST")
        r.add_header('Content-Type', 'application/json')
        r.add_header('Origin', 'http://premium.to')
        r.add_header('Referer', 'http://premium.to')
        r.set_raw_payload(json.dumps({
            "u": Config.get("user"),
            "p": Config.get("password"),
            "r": True
        }))
        response = r.send()
        return response.status_code == 200

    @cache(10*60)
    def handle(self, link):
        request_link = "http://premium.to/getfile.php?link=" + link.split("://", 1)[1]
        r = Request.Request(request_link)
        r.add_header('Referer', 'http://premium.to')
        h = r.open_for_user()
        # If there is any error, premium.to will send a 200 response.
        # (I guess they couldn't remember the function for setting response codes or whatever).
        if h.geturl() is not request_link:
            # If there was a redirect, we can be almost certain that there won't be an error message behind the link.
            return h
        # Otherwise - who knows what happens?
        try:
            for header in h.headers:
                # That's a good sign:
                if header.lower.startswith("content-disposition"):
                    return h
                # Cross your fingers!
                if header.lower().startswith("content-length"):
                    # Nobody wants to download smaller files anyway.
                    if header.split(":", 1)[1].strip() > 10000:  # 10KB
                        return h
            # Okay, now we just give up. Hopefully, we don't print the file to the console here.
            log.error("Downloading from premium.to failed: " + h.read().decode("utf-8"))
        except:
            pass
        raise Errors.PluginError
