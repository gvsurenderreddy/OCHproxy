class RequestError(Exception):
    message = "Unknown error occured"
    code = 1
    http_code = 500


class PluginError(RequestError):
    message = "Internal error - No plugin was able to process link."
    code = 2


class NoSuchUserError(RequestError):
    message = "Wrong username or password"
    code = 3
    http_code = 401


class TemporarilyImpossibleError(RequestError):
    message = "Unable to reach hoster, please retry later..."
    code = 4


class InvalidLinkError(RequestError):
    message = "Invalid link. Either the link has been deleted or it never existed in the first place."
    code = 5
