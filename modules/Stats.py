from texttable import Texttable
import humanize

__all__ = ["make_stats"]


def make_stats(data, name):
    table = Texttable()
    table.set_cols_align(["r", "c", "c"])
    table.add_rows([["Name", "Traffic total", "Avg bandwidth"]] + sort(get_stats_for(data, name)), True)
    print "Traffic statistics for all " + name + "s:"
    print table.draw() + "\n"


def get_stats_for(traffic, name):
    return [[t[0].strip(name + "/"), h(t[1][0]), h(t[1][0]/t[1][1]) + "/s"] for t in traffic.iteritems() if
            t[0].startswith(name + "/")]


def sort(stats):
    return sorted(stats, key=lambda x: x[1])


h = humanize.naturalsize
