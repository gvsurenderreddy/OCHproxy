from pluginbase import PluginBase
import time
from modules.BasePlugin import BasePlugin
from modules.Config import Config
from modules.Errors import PluginError
from modules.Log import log


def configured(hoster):
    need = hoster.config_values
    for n in need:
        if not Config.get("hoster/" + hoster.plugin_name + "/" + n):
            return False
    return True


class Hoster(object):
    hoster = []
    downloads = {}
    handled = {}
    plugin_source = None

    def __init__(self):
        plugin_base = PluginBase(package='hoster.plugins')
        Hoster.plugin_source = plugin_base.make_plugin_source(
            searchpath=['./hoster'])
        with Hoster.plugin_source:
            for p in Hoster.plugin_source.list_plugins():
                h = Hoster.plugin_source.load_plugin(p)
                if not hasattr(h, p):
                    log.debug("Plugin " + p + " is invalid (No class named " + p + "in module)")
                    continue
                if not Config.get("hoster/" + p + "/active", False):
                    continue
                h = getattr(h, p)()
                h.plugin_name = p
                if not isinstance(h, BasePlugin):
                    log.error("Plugin " + p + " is invalid (Not extending BasePlugin)")
                    continue
                log.debug("Loaded plugin " + p)
                Hoster.hoster.append(h)
                for n in h.config_values:
                    if not Config.get("hoster/" + p + "/" + n):
                        print "Hoster", p, \
                            "needs a", n + ". You need to add a", n, "for", p, "to config.json " \
                                                                               "to use the plugin."

    @staticmethod
    def handle_link(link):
        okay = [h for h in Hoster.hoster if
                h.match(link) and configured(h) and Config.get("hoster/" + h.plugin_name + "/active", False)]
        if len(okay) < 1:
            print "Can't handle link", link, "because no hoster wants to do it"
            return None
        priorized = []
        for hoster in okay:
            priorized.append(((hoster.priority * hoster.get_downloaded_bytes()) + (10 * hoster.get_badness()), hoster))
        priorized = sorted(priorized, key=lambda x: x[0])
        # Try all plugins until there is no plugin left
        i = 0
        download = None
        wasted = {}
        while i < len(priorized):
            start = time.time()
            try:
                download = priorized[i][1].handle(link)
                break
            except PluginError:
                i += 1
            wasted[priorized[i][1]] = (time.time() - start)
        if download is None:
            print priorized[0][1].plugin_name, "wasn't able to process", link
            raise PluginError
        for k, v in wasted.iteritems():
            k.add_badness(v)
        return priorized[0][1], download

Hoster()
