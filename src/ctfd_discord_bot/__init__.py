import asyncio
import traceback
from typing import Any

import discord
from aiohttp import ClientSession, ClientTimeout
from discord import app_commands
from discord.ext import commands
from loguru import logger

from ctfd_discord_bot.utils.environment import BotMode, Config


class CTFdBot(commands.Bot):
    def __init__(self, config: Config):
        self.config = config

        intents = discord.Intents.default()
        super().__init__(command_prefix=".", intents=intents, help_command=None)

    async def setup_hook(self):
        self.tree.on_error = self.on_app_command_error

        COGS = ["general", "ctfd"]

        for cog in COGS:
            await self.load_extension(f"{__name__}.cogs.{cog}")
            logger.debug(f"Loaded: bot.cogs.{cog}")

        synced = await self.tree.sync()
        logger.success(f"Synced {len(synced)} Slash Commands globally.")
        logger.debug(f"Synced: {[cmd.name for cmd in synced]}")

    async def on_ready(self):
        if (
            self.config.bot_mode == BotMode.PRODUCTION
            and self.config.push_url is not None
        ):
            asyncio.create_task(self._push_monitor_task())
            logger.info("Started push monitor task for Uptime Kuma")

    async def _push_monitor_task(self):
        """Background task that calls the push URL every 60 seconds."""
        if self.config.push_url is None:
            return

        while True:
            try:
                push_url = self.config.push_url

                async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                    async with session.get(push_url) as response:
                        if response.status == 200:
                            logger.debug("Successfully sent heartbeat to Uptime Kuma")
                        else:
                            logger.warning(
                                f"[Uptime Kuma] RuntimeError: Push returned status {response.status}."
                            )
            except Exception as exc:
                logger.error(f"[Uptime Kuma] {type(exc).__name__}: {exc}")

            await asyncio.sleep(60)

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        async def response_func(*args: Any, **kwargs: Any):
            # for some reason, just checking interaction.response.is_done does not work
            # and interaction.followup is in invalid state until a response is sent
            try:
                await interaction.response.send_message(*args, **kwargs)
            except discord.InteractionResponded:
                await interaction.followup.send(*args, **kwargs)

        if isinstance(error, app_commands.CommandInvokeError):
            original = error.original
            err_traceback = error.original.__traceback__
            error_loc = error.command.name

            if err_traceback is not None:
                while err_traceback.tb_next is not None:
                    err_traceback = err_traceback.tb_next

                frame = err_traceback.tb_frame
                while f"src/{__name__}" not in frame.f_code.co_filename.replace(
                    "\\", "/"
                ):
                    frame = frame.f_back
                    if frame is None:
                        break

                if frame is not None:
                    error_loc += f" - {frame.f_code.co_qualname}:{frame.f_lineno}"

            logger.error(f"[{error_loc}] {type(original).__name__}: {original}")

            extra = ""
            if self.config.bot_mode == BotMode.DEVELOPMENT:
                extra = f"\n```{''.join(traceback.format_exception(error.original))}```"

            await response_func(
                "An unexpected internal error occurred while executing the command"
                + extra,
                ephemeral=True,
            )

        elif isinstance(error, app_commands.CommandOnCooldown):
            await response_func(
                "This command is on cooldown, please try again later.", ephemeral=True
            )

        elif isinstance(error, app_commands.CheckFailure):
            await response_func(
                "You don't have permission to use this command.", ephemeral=True
            )

        else:
            logger.error(f"[Bot Error] {type(error).__name__}: {error}")

            extra = ""
            if self.config.bot_mode == BotMode.DEVELOPMENT:
                extra = f"\n```{''.join(traceback.format_exception(error))}```"

            await response_func(
                "An unknown error occurred." + extra,
                ephemeral=True,
            )
