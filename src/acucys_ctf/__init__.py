import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from acucys_ctf.utils.environment import BotMode, Config


class ACUCySCTFBot(commands.Bot):
    def __init__(self, config: Config):
        self.config = config

        intents = discord.Intents.default()
        super().__init__(command_prefix=".", intents=intents)

    async def setup_hook(self):
        self.tree.on_error = self.on_app_command_error

        COGS = ["general", "ctfd"]

        for cog in COGS:
            await self.load_extension(f"acucys_ctf.cogs.{cog}")
            logger.info(f"Loaded: bot.cogs.{cog}")

        synced = await self.tree.sync()
        logger.success(f"Synced {len(synced)} Slash Commands globally.")
        logger.debug(f"Synced: {[cmd.name for cmd in synced]}")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandInvokeError):
            original = error.original
            logger.error(
                f"[{error.command.name}] {type(original).__name__}: {original}"
            )

            extra = ""
            if self.config.bot_mode == BotMode.DEVELOPMENT:
                extra = f"\n```{original}```"

            await interaction.followup.send(
                "An unexpected internal error occurred while executing the command"
                + extra,
                ephemeral=True,
            )

        elif isinstance(error, app_commands.CheckFailure):
            await interaction.followup.send(
                "You don't have permission to use this command.", ephemeral=True
            )

        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(
                "This command is on cooldown, please try again later.", ephemeral=True
            )

        else:
            logger.error(f"[Bot Error] {type(error).__name__}: {error}")

            extra = ""
            if self.config.bot_mode == BotMode.DEVELOPMENT:
                extra = f"\n```{error}```"

            await interaction.followup.send(
                "An unknown error occurred." + extra,
                ephemeral=True,
            )
