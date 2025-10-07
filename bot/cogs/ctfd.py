# import os
# import aiohttp
# import asyncio
from bot.utils.ctfd_api import CTFd_API

import discord
from discord import app_commands
from discord.ext import commands


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
                color=discord.Color.gold()
            )

            for i, entry in enumerate(scoreboard[:10], start=1):  # top 10
                name = entry.get("name", "Unknown")
                score = entry.get("score", 0)
                embed.add_field(name=f"{i}. {name}", value=f"*{score} points*", inline=False)

            await interaction.followup.send(embed=embed)

        except Exception:
            await interaction.followup.send("An unexpected error occurred while fetching the scoreboard.", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(CtfD(client))
