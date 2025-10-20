import os
import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from loguru import logger

from bot.utils.environment import ENV_BOT_TOKEN


# ---------------------
# logging
# ---------------------

log_dir = './logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.log')
logger.add(
    os.path.join(log_dir, log_filename), 
    level="DEBUG", 
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}", 
    rotation="2 MB"
)



# ---------------------
# discord bot
# ---------------------

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=".", intents=intents)

    # the proper way to do this:
    #   https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=setup_hook#discord.ext.commands.Bot.setup_hook
    async def setup_hook(self):
        for filename in os.listdir("./bot/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"bot.cogs.{filename[:-3]}")
                logger.info(f"Loaded: bot.cogs.{filename[:-3]}")

        synced = await self.tree.sync()
        logger.success(f"Synced {len(synced)} Slash Commands globally.")
        logger.debug(f"Synced: {[cmd.name for cmd in synced]}")

client = MyBot()

async def main():
    async with client:
        await client.start(ENV_BOT_TOKEN, reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())
