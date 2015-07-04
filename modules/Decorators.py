from modules.Auth import Auth


def needs_auth(func):
    def dec(self, *args):
        user = Auth.auth(self.parse_params(), self.client_address)
        if user is None:
            self.print_debug("Request could not be authenticated")
            self.send_error(401)
            return
        func(self, *args, user=user)
    return dec

