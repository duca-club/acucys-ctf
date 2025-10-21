import os
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse, urlunparse

from acucys_ctf.utils.errors import ConfigError


def get_env_var(name: str, *, required: bool = True) -> str:
    value = os.getenv(name)

    if required and value is None:
        raise ConfigError(f"Missing required environment variable: {name}")

    if value is not None:
        return value.strip()

    return ""


def normalize_url(url: str) -> str:
    (scheme, netloc, path, _, _, _) = urlparse(url, scheme="https")

    path = path.rstrip("/")
    if netloc == "":
        netloc, path = path.split("/", 1)

    return urlunparse((scheme, netloc, path, "", "", ""))


class BotMode(StrEnum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


@dataclass
class Config:
    ctfd_instance_url: str
    ctfd_access_token: str
    bot_token: str
    bot_mode: BotMode = BotMode.DEVELOPMENT

    def __init__(self):
        bot_mode = get_env_var("BOT_MODE", required=False).lower()
        if bot_mode != "":
            try:
                self.bot_mode = BotMode(bot_mode)
            except ValueError:
                raise ConfigError(f"Invalid bot mode: {bot_mode}")

        self.bot_token = get_env_var("BOT_TOKEN")
        self.ctfd_access_token = get_env_var("CTFD_ACCESS_TOKEN")
        self.ctfd_instance_url = normalize_url(get_env_var("CTFD_INSTANCE_URL"))
