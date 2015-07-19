import inspect
import logging
from modules.Config import Config


class ServerLogAdapter(logging.LoggerAdapter):
    thread_local = None

    def process(self, msg, kwargs):
        if ServerLogAdapter.thread_local is None or not Config.get("app/debug", False):
            return msg, kwargs
        return '<Request#%s from %s (%s)> %s' % (ServerLogAdapter.thread_local.id,
                                                 ServerLogAdapter.thread_local.remote[0],
                                                 ServerLogAdapter.thread_local.user, msg), kwargs


if Config.get("app/debug", False):
    level = logging.DEBUG
else:
    level = logging.ERROR

fh = logging.FileHandler('ochproxy.log')
fh.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)

logger = logging.getLogger()
logger.setLevel(level)
logger.addHandler(ch)
logger.addHandler(fh)

log = ServerLogAdapter(logger, {})

def log_method(func):

    def dec(*args, **kwargs):
        if Config.get("app/debug", False):
            callargs = inspect.getcallargs(func, *args, **kwargs)
            fname = func.__name__
            if "self" in callargs:
                fname = callargs.pop("self").__class__.__name__ + "." + fname
            log.debug("Calling " + fname + "(" + callargs.__repr__() + ")")
        return func(*args, **kwargs)
    return dec
