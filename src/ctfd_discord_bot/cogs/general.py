import time
from datetime import timedelta
from platform import python_version

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from ctfd_discord_bot import CTFdBot


class General(commands.Cog):
    start_time: float | None = None

    def __init__(self, client: CTFdBot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        if self.client.user is None:
            raise discord.errors.ClientException("Unable to get client's name!")
        else:
            logger.info(f"Logged in as {self.client.user.name}")

        logger.info(f"Discord.py API version: {discord.__version__}")
        logger.info(f"Python version: {python_version()}")

        self.start_time = time.time()

        # bot presence
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing, name=self.client.config.event_name
            )
        )

        logger.success("Bot is ready!")

    @app_commands.command(
        name="uptime", description="Displays how long the bot has been running."
    )
    async def uptime(self, interaction: discord.Interaction):
        if self.start_time is None:
            await interaction.response.send_message(
                "Uptime tracking has not started yet. Please wait a moment.",
                ephemeral=True,
            )
            return

        current_time = time.time()
        elapsed = int(round(current_time - self.start_time))
        uptime_text = str(timedelta(seconds=elapsed))

        embed = discord.Embed(
            title=":clock: Uptime",
            description=f"The bot has been running for `{uptime_text}`.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="feedback", description="Provide feedback for the bot or CTF."
    )
    async def feedback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Here is the CTF and bot feedback link: {self.client.config.feedback_url}",
            ephemeral=True,
        )

    @app_commands.command(
        name="help", description="Lists all commands and their usage."
    )
    async def help(self, interaction: discord.Interaction):
        commands = await self.client.tree.fetch_commands()
        command_info = ""

        for command in commands:
            command_info += f"`/{command.name}"

            option_info = ""
            for option in command.options:
                if option.required:  # type: ignore
                    command_info += f" <{option.name}>"
                    option_info += (
                        f"\t`{option.name}` (Required) - {option.description}\n"
                    )
                else:
                    command_info += f" [{option.name}]"
                    option_info += (
                        f"\t`{option.name}` (Optional) - {option.description}\n"
                    )

            command_info += f"` - {command.description}\n{option_info}\n"

        embed = discord.Embed(
            title=f"{self.client.config.event_name} Bot Help",
            description=f"""
Welcome to the {self.client.config.event_name} bot!
You can use this bot to register for the CTF, and view various bits of information about it.
The following are all the commands supported by this bot:

"""
            + command_info,
            color=discord.Color.teal(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: CTFdBot):
    await client.add_cog(General(client))
