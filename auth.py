
# noinspection PyUnusedLocal
def auth(params, ip):
    """
    Custom authentication could be done here.
    :type ip: str
    :type params: dict
    :param params: All of the GET-parameters that were in the request
    :param ip:  The IP-address of the client.
    :return: True if the client is allowed do download, False otherwise
    """
    return True
