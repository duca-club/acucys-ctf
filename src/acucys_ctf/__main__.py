import asyncio
import os
from datetime import datetime

import dotenv
from loguru import logger

from acucys_ctf import ACUCySCTFBot


async def async_main():
    async with ACUCySCTFBot() as client:
        await client.start(client.config.bot_token, reconnect=True)


def main():
    dotenv.load_dotenv()

    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.log")
    logger.add(
        os.path.join(log_dir, log_filename),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="2 MB",
    )

    asyncio.run(async_main())


if __name__ == "__main__":
    main()
