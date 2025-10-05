import os
import aiohttp
import asyncio

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

        access_token = os.getenv("CTFD_ACCESS_TOKEN")
        if not access_token:
            await interaction.followup.send("Server error! Big OOF!", ephemeral=True)
            return

        ENV_CTFD_INSTANCE_URL = os.getenv("CTFD_INSTANCE_URL")
        url = f"{ENV_CTFD_INSTANCE_URL}/api/v1/scoreboard"
        headers = {
            "Authorization": f"Token {access_token}",
            "Accept": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=10) as response: # type: ignore
                    if response.status == 200:
                        data = await response.json()
                        scoreboard = data.get("data", [])

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

                    else:
                        await interaction.followup.send(f"⚠️ Failed to fetch scoreboard (HTTP {response.status})", ephemeral=True)

            except asyncio.TimeoutError:
                await interaction.followup.send("Request timed out. Try again later!", ephemeral=True)

            # except aiohttp.ClientError:
            except Exception:
                await interaction.followup.send(f"Oopsie Error!", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(CtfD(client))
