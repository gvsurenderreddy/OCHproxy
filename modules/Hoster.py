from pluginbase import PluginBase
import time
from modules.Config import Config


def configured(hoster):
    need = hoster[1].needs()
    for n in need:
        if not Config.get("hoster/" + hoster[0] + "/" + n):
            return False
    return True


class Hoster:
    hoster = []
    plugin_source = None
    downloads = {}
    handled = {}

    def __init__(self):
        global plugin_source
        plugin_base = PluginBase(package='hoster.plugins')
        plugin_source = plugin_base.make_plugin_source(
            searchpath=['./hoster'])
        with plugin_source:
            for p in plugin_source.list_plugins():
                h = plugin_source.load_plugin(p)
                if not hasattr(h, "match") or not hasattr(h, "handle") or not hasattr(h, "priority"):
                    continue
                Config.get("hoster/" + p + "/active", False)
                self.hoster.append((p, h))
                if hasattr(h, "setup"):
                    print "Setting up hoster", p
                    h.setup()
                if not hasattr(h, "needs"):
                    continue
                for n in h.needs():
                    if not Config.get("hoster/" + p + "/" + n):
                        print "Hoster", p, \
                            "needs a", n + ". You need to add a", n, "for", p, "to config.json " \
                                                                               "to use the plugin (no restart needed)."

    def handle_link(self, link):
        if link in Hoster.handled:
            t, result = Hoster.handled[link]
            if (t+30*60) > time.time():
                return result
        okay = [h[1] for h in self.hoster if
                h[1].match(link) and configured(h) and Config.get("hoster/" + h[0] + "/active", False)]
        if len(okay) < 1:
            print "Can't handle link", link, "because no hoster wants to do it"
            return None
        priorized = []
        for hoster in okay:
            priorized.append((hoster.priority() * self.get_downloads_for(hoster), hoster))
        priorized = sorted(priorized, key=lambda x: x[0])
        download = priorized[0][1].handle(link)
        if download is None:
            print priorized[0][1], "wasn't able to process", link
            return None
        self.increase_downloads_for(priorized[0][1])
        Hoster.handled[link] = (time.time(), download)
        return download

    def get_downloads_for(self, hoster):
        if hoster not in self.downloads:
            self.downloads[hoster] = 0
        return self.downloads[hoster]

    def increase_downloads_for(self, hoster):
        if hoster not in self.downloads:
            self.downloads[hoster] = 0
        self.downloads[hoster] += 1
