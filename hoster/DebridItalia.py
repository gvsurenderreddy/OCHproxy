from modules import Request
from modules.Config import Config

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


def needs():
    return ["hoster/debriditalia/password", "hoster/debriditalia/user"]


def priority():
    return 2


def match(link):
    # TODO
    hoster = link.split("://")[1]
    hoster = hoster.split("/")[0]
    hoster = hoster.strip("www.")
    if str.upper(hoster) in map(str.upper, supported):
        return handle(link) is not None
    return False


def handle(link):
    r = Request.Request("http://www.debriditalia.com/api.php", payload={
        'generate': "on",
        'link': link,
        'p': Config.get("hoster/debriditalia/password"),
        'u': Config.get("hoster/debriditalia/user")}).send()
    if "ERROR:" not in r.text:
        return Request.Request(url=r.text.strip())
    return None
