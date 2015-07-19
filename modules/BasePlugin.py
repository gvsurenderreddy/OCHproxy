# coding=utf-8
import time
from modules import Errors
from modules import Decorators

Errors = Errors
cache = Decorators.cache_result
class BasePlugin(object):
    """
    If you write a class that extends this class and put it in the `hoster` directory, it's a hoster plugin as far as
    OCHproxy is concerned.
    The name of the class *must* match the file name.
    Please not that OCHproxy totally trusts plugins and doesn't execute them in a sandbox or something like that.
    This means that you should check your plugin for bugs. If you're asking "What's the worst thing that can happen?" -
    well, I guess you could crash OCHproxy (or if you know what you're doing you could try to get the whole system in
    trouble).
    In the future™, it might be possible to have multiple instances of your plugin running with different accounts
    so you should correctly use instance attributes instead of class attributes if they should be different across
    instances.
    Your plugin will be reloaded every time the config changes, so take a look at `persist` if you want to persist
    attributes during reloads.

    TODO: Logging?

    Class Attributes:
        - `hostname`:
            The hostname for which the plugin is responsible or a list of hostnames for which the plugin is responsible.
        - `priority`:
            A positive integer number. The smaller it is, the more likely will the plugin be chosen.
            To be more precise: The plugin with the lowest $priority * bytes downloaded$ will be chosen.
            You should use the constants in Hoster.Priority.
        - `config_values`:
            A list of config values your plugin will use. Use a tuple in the format (key, value) to set a default value
            if it is optional. If a non-optional config item is not provided, your plugin will not be instantiated.

    """

    priority = -1
    config_values = []
    cache = {}
    hostname = []

    def __init__(self):
        """
        You might want to log the user in here. You could also set the number of downloaded bytes .
        Don't raise any errors though, just silently deactivate the plugin if anything went wrong.
        If the login data is invalid, just deactivate forever, your plugin will be reloaded once the config values for
        it change.
        """
        self.deactivated_until = 0
        self.downloaded = 0

    def match(self, link):
        """
        The preferred way to define which links your plugin can download is to define a class attribute
        `hostname` that contains the hostname of hosters the plugin can download from.
        You may override this method if you want to have finer control of the links that get passed to handle.
        :param link: A link
        :return: True if this plugin can handle the link, False otherwise
        """

        if isinstance(self.__class__.hostname, basestring):
            self.__class__.hostname = [self.__class__.hostname]
        for h in self.__class__.hostname:
            try:
                if link.split("://", 1)[1].split("/", 1)[0].endswith(h):
                    return True
            except (NameError, TypeError, IndexError):
                pass
        return False

    def handle(self, link):
        """
        A plugin must override this method. It is abstract (well, not really, but it would be abstract if Python had
        abstract methods).
        If the link is invalid, deleted or something like that, raise an InvalidLinkError.
        If there are temporary errors (*not* on our side) that prevent the download (e.g. server maintenance),
        raise a TemporarilyImpossibleError.
        If your plugin won't be able to handle any link in the near future (e.g. the traffic limit is reached),
        deactivate your plugin and raise a PluginError. OCHproxy will then try to find another plugin to handle the link
        or fail the request.
        Please use PyQuery to parse HTML if that makes sense.
        :param link: A link to the resource the user wants to download.
        :return: An instance of Request that returns the data of the download once opened.
        """
        raise NotImplementedError

    def deactivate(self, how_long=None):
        """
        Deactivates the plugin for `how_long` seconds or until reload if how_long is omitted.
        You can override this method if you want, but you then might need to override is_active too.
        :param how_long: After how many seconds the plugin should be activated again.
        :return: None
        """
        if how_long is None:
            # float(inf) is bigger than any number
            self.deactivated_until = float("inf")
        self.deactivated_until = time.time() + how_long

    def is_active(self):
        """
        Determines if the plugin is active. Plugins are active once they are loaded and remain active until
        deactivate gets called.
        You can override this method if you have any special conditions (e.g. only if there is a full moon at the server
        location) that determine if the plugin is active or not.
        This method gets called quite often (once on every request to the /get and the /links endpoint) so you shouldn't
        do any expensive stuff (e.g. sending a request to a web page with a moon calendar) in here.
        :return: True if the plugin is active, False otherwise.
        """
        return time.time() > self.deactivated_until

    def get_downloaded_bytes(self):
        """
        Get the number of downloaded bytes.
        :return: Number of Bytes already downloaded.
        """
        return self.downloaded

    def add_downloaded_bytes(self, x):
        """
        Add x Bytes to the counter.
        :param x: Number of Bytes just downloaded
        :return: Nothing
        """
        self.downloaded += x


class Priority(object):
    DIRECT_UNLIMITED = 1
    DIRECT_LIMITED = 4
    MULTI_UNLIMITED = 5
    MULTI_LIMITED = 8
