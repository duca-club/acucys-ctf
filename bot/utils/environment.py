# this file will validate all the ernvironment vairables before starting the bot

import os
import sys
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

__env_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not __env_BOT_TOKEN:
    logger.error("Environment variable `BOT_TOKEN` is not set properly inside the `.env` file!")
    sys.exit(-1)
ENV_BOT_TOKEN = __env_BOT_TOKEN

__env_CTFD_INSTANCE_URL = os.getenv("CTFD_INSTANCE_URL")
if __env_CTFD_INSTANCE_URL or isinstance(__env_CTFD_INSTANCE_URL, str):
    if __env_CTFD_INSTANCE_URL.endswith("/"):
        __env_CTFD_INSTANCE_URL = __env_CTFD_INSTANCE_URL[:-1]
    if not __env_CTFD_INSTANCE_URL.startswith("http"):
        __env_CTFD_INSTANCE_URL = "https://" + __env_CTFD_INSTANCE_URL
else:
    logger.error("Environment variable `CTFD_INSTANCE_URL` is not set properly inside the `.env` file!")
    sys.exit(-1)
ENV_CTFD_INSTANCE_URL = __env_CTFD_INSTANCE_URL

__env_CTFD_ACCESS_TOKEN = os.getenv("CTFD_ACCESS_TOKEN")
if not __env_CTFD_ACCESS_TOKEN:
    logger.error("Environment variable `CTFD_ACCESS_TOKEN` is not set properly inside the `.env` file!")
    sys.exit(-1)
ENV_CTFD_ACCESS_TOKEN = __env_CTFD_ACCESS_TOKEN




