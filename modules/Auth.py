
class Auth:
    user = {}
    try:
        with open('users.txt') as f:
            for x in f.readlines():
                u, p = x.strip().split(":", 1)
                user[u] = p
    except (IOError, OSError):
        pass

    @staticmethod
    def auth(params, ip):
        if "user" not in params or "password" not in params:
            return False
        if params["user"][0] not in Auth.user:
            return False
        password = params["password"][0]
        return Auth.user[params["user"][0]] == password
