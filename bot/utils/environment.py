# this file will validate all the ernvironment vairables before starting the bot

import os
import sys
from loguru import logger
from dotenv import load_dotenv

from bot.utils import errors

load_dotenv()

class Config:
    @staticmethod
    def _get_env_var(name: str, required: bool = True) -> str:
        value = os.getenv(name)

        if not(value):
            if required:
                logger.error(f"Environment variable `{name}` is missing or empty in the `.env` file!")
                raise errors.ConfigError(f"Missing required environment variable: {name}")
            else:
                logger.warning(f"Environment variable `{name}` is missing or empty in the `.env` file!")
                # optional... just warn the user and neglect
        
        if value:
            return value.strip()

        return ""

    @staticmethod
    def _normalize_url(url: str, name: str = "") -> str:
        url = url.strip()

        if url.endswith("/"):
            url = url[:-1]

        if not url.startswith(("http://", "https://")):
            if name:
                logger.warning(f"{name} missing scheme... Assuming HTTPS.")
            else:
                logger.warning(f"URL is missing scheme... Assuming HTTPS.")
            url = "https://" + url

        return url

    @classmethod
    def load(cls):
        try:
            ctfd_url = cls._get_env_var("CTFD_INSTANCE_URL")
            ctfd_url_normalized = cls._normalize_url(url=ctfd_url, name="CTFD_INSTANCE_URL")
            
            ctfd_token = cls._get_env_var("CTFD_ACCESS_TOKEN")
            bot_token = cls._get_env_var("BOT_TOKEN")

            # TODO: maybe get rid of this part... maybe not?
            logger.success("Environment variables loaded successfully!")
            logger.debug(f"CTFd URL: {ctfd_url_normalized}")
            logger.debug(f"CTFd Token: {ctfd_token}")
            logger.debug(f"Bot Token: {bot_token}")

            return {
                "CTFD_INSTANCE_URL": ctfd_url_normalized,
                "CTFD_ACCESS_TOKEN": ctfd_token,
                "BOT_TOKEN": bot_token,
            }

        except errors.ConfigError as e:
            logger.critical(str(e))
            sys.exit(1)
        except Exception as e:
            logger.exception(f"Unexpected error during configuration load: {e}")
            sys.exit(1)


# global config
CONFIG = Config.load()

# init here for convenience
ENV_CTFD_INSTANCE_URL = CONFIG["CTFD_INSTANCE_URL"]
ENV_CTFD_ACCESS_TOKEN = CONFIG["CTFD_ACCESS_TOKEN"]
ENV_BOT_TOKEN = CONFIG["BOT_TOKEN"]
