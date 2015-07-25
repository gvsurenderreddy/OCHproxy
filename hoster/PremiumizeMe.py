from modules.Request import Request
from modules.BasePlugin import *
from modules.Config import Config
from modules.Log import log

class PremiumizeMe(BasePlugin):
    priority = Priority.MULTI_LIMITED
    config_values = ["user-id", "PIN"]

    def __init__(self):
        super(PremiumizeMe, self).__init__()
        self.account_status()
        # Now this is a decent API!
        r = Request("https://api.premiumize.me/pm-api/v1.php", payload={
            "method": "hosterlist",
            "params[login]": Config.get("user-id"),
            "params[pass]": Config.get("PIN")
        }).send().json
        if r["status"] is not 200:
            log.error("premiumize.me: Receiving hoster list failed: " + r["statusmessage"])
            self.deactivate()
            return
        PremiumizeMe.hostname = r["result"]["tldlist"]

    def account_status(self):
        r = Request("https://api.premiumize.me/pm-api/v1.php", payload={
            "method": "accountstatus",
            "params[login]": Config.get("user-id"),
            "params[pass]": Config.get("PIN")
        }).send().json
        if r["status"] is not 200:
            log.error("premiumize.me: Unable to get account status. Deactivating.")
            self.deactivate()
            return
        if r["result"]["type"] is "free":
            log.error("premiumize.me: Account is free account. Deactivating.")
            self.deactivate()
            return

    @cache(10*60)
    def handle(self, link):
        r = Request("https://api.premiumize.me/pm-api/v1.php", payload={
            "method": "directdownloadlink",
            "params[login]": Config.get("user-id"),
            "params[pass]": Config.get("PIN"),
            "params[link]": link
        }).send().json
        if r["status"] is 200:
            return Request(r["result"]["location"])
        if r["status"] is 400 or r["status"] is 404:
            raise Errors.InvalidLinkError
        if r["status"] in [401, 402, 403]:
            log.error("premiumize.me: " + r["statusmessage"] + " deactivating.")
            self.deactivate()
            return
        raise Errors.PluginError
