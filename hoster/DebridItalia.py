from modules import Request
from modules.BasePlugin import *
from modules.Config import Config


class DebridItalia(BasePlugin):
    priority = Priority.MULTI_UNLIMITED
    config_values = ["user", "password"]
    supported = [
        "1Fichier.com",
        "2Shared.com",
        "4shared.com",
        "Backin.net",
        "Brazzers.com",
        "Cloudzilla.to",
        "Crockdown.com",
        "Datafile.com",
        "Depfile.com",
        "Easybytez.com",
        "Ex-Load.com",
        "Extmatrix.com",
        "Fileboom.com",
        "Filemoney.com",
        "Filesmonster.com",
        "Fileparadox.in",
        "Rapidsonic.com",
        "FilePost.com",
        "Filesflash.com",
        "Filespace.com",
        "Inclouddrive.com",
        "Letitbit.net",
        "Megashares.com",
        "Netload",
        "NowDownload.ch",
        "Nowvideo.co",
        "Rapidgator.net",
        "Rockfile.eu",
        "Ryushare.com",
        "Salefiles.com",
        "Secureupload.eu",
        "Share-Online.biz",
        "Storedeasy.com",
        "Tusfiles.net",
        "Uploaded.to",
        "Uploaded.net",
        "UploadRocket.net",
        "Uptobox.com"
    ]

    def __init__(self):
        super(DebridItalia, self).__init__()

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

    def match(self, link):
        # TODO
        try:
            hoster = link.split("://")[1]
            hoster = hoster.split("/")[0]
            hoster = hoster.strip("www.")
            if str.upper(hoster) in map(str.upper, self.supported):
                return self.handle(link) is not None
        except IndexError:
            return False
        return False
