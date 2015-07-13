
class Auth(object):
    class User(object):

        def __init__(self, username, password):
            self.password = password
            self.connections = 0
            self.username = username

    user = {}
    try:
        with open('users.txt') as f:
            for x in f.readlines():
                u, p = x.strip().split(":", 1)
                user[u] = User(u, p)
    except (IOError, OSError):
        pass

    @staticmethod
    def auth(params, ip):
        if "user" not in params or "password" not in params:
            return None
        if params["user"][0] not in Auth.user:
            return None
        password = params["password"][0]
        if Auth.user[params["user"][0]].password != password:
            return None
        return Auth.user[params["user"][0]]

