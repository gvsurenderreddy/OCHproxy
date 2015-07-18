import time
from modules import Errors
from modules.Auth import Auth


def needs_auth(func):
    def dec(self, *args):
        user = Auth.auth(self.server.parse_params(), self.server.client_address)
        if user is None:
            self.server.print_debug("Request could not be authenticated")
            raise Errors.NoSuchUserError
        func(self, *args, user=user)
    return dec

# "Yo dawg I heard you like closures..."
def cache_result(c=30*60):
    def real_decorator(func):
        def dec(self, link):
            if link in self.cache:
                when, what = self.cache[link]
                if when + c > time.time():
                    return what
            result = func(self, link)
            self.cache[link] = (time.time(), result)
            return result
        return dec
    return real_decorator
