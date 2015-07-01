from pluginbase import PluginBase
from modules.Config import Config


def configured(hoster):
    need = hoster.needs()
    for n in need:
        if not Config.get(n):
            return False
    return True


class Hoster:
    hoster = []
    plugin_source = None
    downloads = {}

    def __init__(self):
        global plugin_source
        plugin_base = PluginBase(package='hoster.plugins')
        plugin_source = plugin_base.make_plugin_source(
            searchpath=['./hoster'])
        with plugin_source:
            for p in plugin_source.list_plugins():
                h = plugin_source.load_plugin(p)
                if h.match is None or h.handle is None or h.priority is None:
                    continue
                self.hoster.append((p, h))
                if h.needs is None:
                    continue
                for n in h.needs():
                    if not Config.get(n):
                        n = n.split("/")[-1]
                        print "Hoster", p, \
                            "needs a", n + ". You need to add a", n, "for", p, "to config.json " \
                                                                               "to use the plugin (no restart needed)."

    def handle_link(self, link):
        okay = [h[1] for h in self.hoster if
                h.match(link) and configured(h) and Config.get("hoster/" + h[0] + "/active", False)]
        if len(okay) < 1:
            print "Can't handle link", link, "because no hoster wants to do it"
            return None
        priorized = []
        for hoster in okay:
            priorized.append((hoster.priority() * self.get_downloads_for(hoster), hoster))
        priorized = sorted(priorized, key=lambda x: x[0])
        # reload(priorized[0][1])
        download = priorized[0][1].handle(link)
        if download is None:
            print priorized[0][1], "wasn't able to process", link
            return None
        self.increase_downloads_for(priorized[0][1])
        return download.open()

    def get_downloads_for(self, hoster):
        if hoster not in self.downloads:
            self.downloads[hoster] = 0
        return self.downloads[hoster]

    def increase_downloads_for(self, hoster):
        if hoster not in self.downloads:
            self.downloads[hoster] = 0
        self.downloads[hoster] += 1
