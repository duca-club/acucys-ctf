from datetime import timedelta
from platform import python_version
from time import time

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from acucys_ctf import ACUCySCTFBot


class General(commands.Cog):
    start_time: float | None = None

    def __init__(self, client: ACUCySCTFBot):
        self.client = client

        # custom help
        # self.client.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.client.user:
            logger.info(f"Logged in as {self.client.user.name}")
        else:
            logger.warning("Unable to get client's name!")
        logger.info(f"Discord.py API version: {discord.__version__}")
        logger.info(f"Python version: {python_version()}")

        self.start_time = time()

        # bot presence
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing, name="ACUCyS CTF"
            )
        )

        logger.success("Bot is ready!")

    @app_commands.command(
        name="uptime", description="Displays how long the bot has been running."
    )
    async def uptime(self, interaction: discord.Interaction):
        if not self.start_time:  # big oof
            await interaction.response.send_message(
                "Uptime tracking has not started yet. Please wait a moment.",
                ephemeral=True,
            )
            return

        current_time = time()
        elapsed = int(round(current_time - self.start_time))
        uptime_text = str(timedelta(seconds=elapsed))

        embed = discord.Embed(
            title=":clock: Uptime",
            description=f"The bot has been running for `{uptime_text}`.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: ACUCySCTFBot):
    await client.add_cog(General(client))
