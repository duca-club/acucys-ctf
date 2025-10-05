import os
import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from loguru import logger
from dotenv import load_dotenv


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
# env vars
# ---------------------

load_dotenv()
ENV_BOT_TOKEN = os.getenv("BOT_TOKEN")


# ---------------------
# discord bot
# ---------------------

client = commands.Bot(command_prefix=".", intents=discord.Intents.all())


@client.tree.command(name="sync", description="Sync Commands Globally")
async def sync(interaction: discord.Interaction):
    synced = await client.tree.sync()
    logger.debug(f"Synced: {synced}")
    logger.success(f'Synced {len(synced)} Slash Commands')
    logger.debug('Command tree synced.')

async def load_extensions():
    for filename in os.listdir('./bot/cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'bot.cogs.{filename[:-3]}')
            logger.info(f"Loaded: bot.cogs.{filename[:-3]}")

async def start_bot():
    async with client:
        await load_extensions()
        await client.start(token=ENV_BOT_TOKEN, reconnect=True)


if __name__ == "__main__":
    asyncio.run(start_bot())
