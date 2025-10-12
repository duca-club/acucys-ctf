import os
from datetime import timedelta
from platform import python_version
from time import time

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger
from bot.utils.environment import is_dev_mode


class General(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        # custom help
        # self.client.remove_command("help")

        self.start_time = None  # for uptime tracking

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

        # todo: remove this after confirming further
        # -----
        # _tmp_filecheck = ".DO_NOT_DELETE.txt"
        # if not os.path.isfile(_tmp_filecheck):
        #     synced = await self.client.tree.sync()
        #     logger.debug(f"Synced: {[(str(item.name)+'-'+str(item.id)) for item in synced]}")
        #     logger.success(f"Synced {len(synced)} Slash Commands")
        #     with open(_tmp_filecheck, "w", encoding="utf-8") as _file:
        #         _file.write(
        #             "Deleting this file and restarting the bot\n"
        #             "will make the bot register its command tree\n"
        #             "once again"
        #         )

        logger.success("Bot is ready!")
    
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if interaction.command:
            logger.error(f"[{interaction.command.name}] {type(error).__name__}: {error}")
        else:
            logger.error(f"[Bot Error] {type(error).__name__}: {error}")

        if isinstance(error, app_commands.CommandInvokeError):
            # original = getattr(error, "original", error)
            await interaction.followup.send("An unexpected internal error occurred while executing the command", ephemeral=True)

        elif isinstance(error, app_commands.TransformerError):
            await interaction.followup.send("Invalid argument or conversion error.", ephemeral=True)
        
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.followup.send("You don't have permission to use this command.", ephemeral=True)
        
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send("This command is on cooldown, please try again later.", ephemeral=True)
        
        else:
            if is_dev_mode():
                await interaction.followup.send(f"An unknown error occurred.\n```{error}```", ephemeral=True)
            else:
                await interaction.followup.send(f"An unknown error occurred.", ephemeral=True)


    @app_commands.command(name="uptime", description="Displays how long the bot has been running.")
    async def uptime(self, interaction: discord.Interaction):
        if not self.start_time: # big oof
            await interaction.response.send_message("Uptime tracking has not started yet. Please wait a moment.", ephemeral=True)
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


async def setup(client: commands.Bot):
    await client.add_cog(General(client))
