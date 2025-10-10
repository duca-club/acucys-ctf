# import os
# import aiohttp
# import asyncio
from bot.utils.ctfd_api import CTFd_API

import discord
from discord import app_commands
from discord.ext import commands
import datetime


class CtfD(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        # custom help
        # self.client.remove_command("help")

        self.start_time = None  # for uptime tracking

    @app_commands.command(name="scoreboard", description="Show the current CTFd scoreboard.")
    async def scoreboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            scoreboard = await CTFd_API.get_scoreboard()
            if not scoreboard:
                await interaction.followup.send("No scoreboard data found.", ephemeral=True)
                return

            embed = discord.Embed(
                title=":trophy: CTFd Scoreboard",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.display_avatar.url) # type: ignore

            for i, entry in enumerate(scoreboard[:10], start=1):  # top 10
                print(entry)
                name = entry.get("name", "Unknown")
                score = entry.get("score", 0)
                members = entry.get("members", [])
                embed.add_field(name=f"{i}. {name}", value=f"Score: *{score} points*\nMembers: *{len(members)}*", inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception:
            await interaction.followup.send("An unexpected error occurred while fetching the scoreboard.", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(CtfD(client))
