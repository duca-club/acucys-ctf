import asyncio
import os
from datetime import datetime

import dotenv
from loguru import logger

from acucys_ctf import ACUCySCTFBot
from acucys_ctf.utils.environment import BotMode, Config


async def async_main(config: Config):
    async with ACUCySCTFBot(config) as client:
        await client.start(config.bot_token, reconnect=True)


def main():
    dotenv.load_dotenv()
    config = Config()

    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.log")
    logger.add(
        os.path.join(log_dir, log_filename),
        level="DEBUG" if config.bot_mode == BotMode.DEVELOPMENT else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="2 MB",
    )

    asyncio.run(async_main(config))


if __name__ == "__main__":
    main()
