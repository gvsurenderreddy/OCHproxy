# Quick test of hoster plugins
from pluginbase import PluginBase

plugin_source = None

def setup_module(module):
    global plugin_source
    plugin_base = PluginBase(package='hoster.plugins')
    plugin_source = plugin_base.make_plugin_source(
        searchpath=['../hoster'])

def test_methods():
    global plugin_source
    with plugin_source:
            for p in plugin_source.list_plugins():
                h = plugin_source.load_plugin(p)
                h.needs()
                assert h.match("https://example.example/dont/match/this") is False
                assert h.priority() > -1
