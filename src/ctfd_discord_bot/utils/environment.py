import os
from dataclasses import MISSING, dataclass, field
from enum import StrEnum
from typing import Any, Self
from urllib.parse import urlparse, urlunparse

from ctfd_discord_bot.utils.errors import ConfigError


def normalize_url(url: str) -> str:
    (scheme, netloc, path, _, _, _) = urlparse(url, scheme="https")

    path = path.rstrip("/")
    if netloc == "":
        netloc, path = path.split("/", 1)

    return urlunparse((scheme, netloc, path, "", "", ""))


class BotMode(StrEnum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"

    @classmethod
    def parse(cls: type[Self], value: str) -> Self:
        try:
            return cls(value.lower())
        except ValueError:
            raise ConfigError("Expected bot mode, got " + value)


def parse_positive_int(value: str) -> int:
    try:
        num = int(value)
    except ValueError:
        raise ConfigError("Expected positive integer, got " + value)

    if num < 0:
        raise ConfigError("Expected positive integer, got " + value)

    return num


@dataclass(frozen=True)
class Config:
    ctfd_instance_url: str = field(metadata={"parser": normalize_url})
    ctfd_access_token: str
    event_name: str
    webhook_url: str
    discord_id_field: int
    bot_token: str
    feedback_url: str
    webhook_frequency: int = field(default=10, metadata={"parser": parse_positive_int})
    api_timeout: int = field(default=5, metadata={"parser": parse_positive_int})
    cache_timeout: int = field(default=60, metadata={"parser": parse_positive_int})
    register_timeout: int = field(default=60, metadata={"parser": parse_positive_int})
    bot_mode: BotMode = field(
        default=BotMode.DEVELOPMENT, metadata={"parser": BotMode.parse}
    )
    push_url: str = field(default=None, metadata={"parser": normalize_url})

    def __init__(self):
        for cur_field in self.__dataclass_fields__.values():
            name = cur_field.name.upper()
            value = os.getenv(name)

            if cur_field.default is MISSING and value is None:
                raise ConfigError(f"Missing required environment variable: {name}")

            if value is not None:

                def parser(val: str) -> Any:
                    return cur_field.type(val)

                if "parser" in cur_field.metadata:
                    parser = cur_field.metadata["parser"]

                object.__setattr__(self, cur_field.name, parser(value.strip()))
