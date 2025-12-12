class ConfigError(Exception):
    """Raised when the environment configuration is invalid."""

    pass


class CTFdError(Exception):
    """Raised when the CTFd API returns and error."""

    pass
