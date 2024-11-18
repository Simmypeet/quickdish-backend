from api.configuration import Configuration


_configuration: None | Configuration = None


def get_configuration() -> Configuration:
    """Use this dependency to get the `State` object"""

    global _configuration

    if _configuration is None:
        _configuration = Configuration()

    return _configuration
