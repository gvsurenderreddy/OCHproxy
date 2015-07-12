from shove import Shove
from modules import Stats

traffic_data = None


# noinspection PyUnusedLocal
def setup_module(module):
    global traffic_data
    traffic_data = Shove('file://../traffic_log/')


def test_server():
    Stats.make_stats(traffic_data, "hoster")


def test_invalid():
    Stats.make_stats(traffic_data, "foo")
