import re
from modules import Request
from modules.Config import Config

link_format = r"https?://(www\.)?share-online.biz/dl/(.*)$"
dls = 0


def needs():
    return ["user", "password"]


def priority():
    return 0


def match(link):
    return re.search(link_format, link) is not None


def handle(link):
    try:
        lid = re.match(link_format, link).group(2)
    except IndexError:
        return Request.Request(url=link)
    r = Request.Request(url="http://api.share-online.biz/account.php",
                        payload={
                            'act': "download",
                            'username': Config.get("user"),
                            'password': Config.get("password"),
                            'lid': lid}).send()
    if r.status_code == 404:
        return Request.Request(url=link)
    lines = r.text.splitlines()
    for line in lines:
        if "URL" in line:
            url = line.split(":", 1)[1].strip()
            return Request.Request(url=url)
    return Request.Request(url=link)
