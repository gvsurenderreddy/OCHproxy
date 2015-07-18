import os


class Auth(object):
    class User(object):

        def __init__(self, username, password):
            self.password = password
            self.connections = 0
            self.username = username

    user = None
    file_date = 0

    @staticmethod
    def load_users():
        try:
            if Auth.user is None or Auth.file_date is not os.stat('users.txt')[8]:
                Auth.file_date = os.stat('users.txt')[8]
                with open('users.txt') as f:
                    for x in f.readlines():
                        u, p = x.strip().split(":", 1)
                        Auth.user[u] = Auth.User(u, p)
        except (IOError, OSError):
            print "could not load users.txt"
            pass

    @staticmethod
    def auth(params, ip):
        Auth.load_users()
        if "user" not in params or "password" not in params:
            return None
        if params["user"][0] not in Auth.user:
            return None
        password = params["password"][0]
        if Auth.user[params["user"][0]].password != password:
            return None
        return Auth.user[params["user"][0]]

