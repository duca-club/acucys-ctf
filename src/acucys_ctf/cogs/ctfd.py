import datetime
import textwrap
import typing

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from acucys_ctf import ACUCySCTFBot
from acucys_ctf.utils.ctfd_api import Challenge, CTFd_API, Score


class ViewScoreboard(discord.ui.View):
    scoreboard: list[Score]
    current_index: int
    showing_list: bool

    def __init__(self, scoreboard: list[Score], current_index: int = 0):
        super().__init__(timeout=180)
        self.scoreboard = scoreboard
        self.current_index = current_index
        self.showing_list = True
        self.update_buttons()

    def update_buttons(self):
        """Enable/disable navigation depending on mode and index."""
        self.left.disabled = self.showing_list or self.current_index <= 0
        self.right.disabled = (
            self.showing_list or self.current_index >= len(self.scoreboard) - 1
        )
        self.list.label = (
            "📋 View Team Details" if self.showing_list else "📋 Back to Team List"
        )

    def get_list_embed(self):
        """Embed showing all teams in the description."""
        embed = discord.Embed(
            title=":trophy: Scoreboard: All Teams",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        # Build a formatted description string
        description_lines: list[str] = []
        for entry in self.scoreboard:
            description_lines.append(
                f"{entry["pos"]}.**{entry["name"]}**: *({entry["score"]} points)*"
            )

        embed.description = "\n".join(description_lines)
        return embed

    def get_team_embed(self):
        """Embed showing a single team."""
        entry = self.scoreboard[self.current_index]
        embed = discord.Embed(
            title=f"🚩 {entry["pos"]}. Team *{entry["name"]}*",
            color=discord.Color.gold(),
            description=f"**Rank**: *{entry["pos"]}*\n**Total Score**: *{entry["score"]}*",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        if entry["members"]:
            member_lines = "\n".join(
                f"• **{m.get('name', 'Unknown')}**: {m.get('score', 0)} pts"
                for m in entry["members"]
            )
            embed.add_field(name="Members", value=member_lines, inline=False)
        else:
            embed.add_field(name="Members", value="No members found.", inline=False)

        embed.set_footer(
            text=f"Team {self.current_index + 1} of {len(self.scoreboard)}"
        )
        return embed

    # ⬅️
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def left(
        self, interaction: discord.Interaction, _button: discord.ui.Button[typing.Self]
    ):
        if not self.showing_list and self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.get_team_embed(), view=self
            )

    # 📋
    @discord.ui.button(label="📋 View Team Details", style=discord.ButtonStyle.primary)
    async def list(
        self, interaction: discord.Interaction, _button: discord.ui.Button[typing.Self]
    ):
        """Toggle between list and single team view."""
        self.showing_list = not self.showing_list
        self.update_buttons()
        embed = self.get_list_embed() if self.showing_list else self.get_team_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    # ➡️
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def right(
        self, interaction: discord.Interaction, _button: discord.ui.Button[typing.Self]
    ):
        if not self.showing_list and self.current_index < len(self.scoreboard) - 1:
            self.current_index += 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.get_team_embed(), view=self
            )


class CtfD(commands.Cog):
    challenge_categories: set[str] = set()

    def __init__(self, client: ACUCySCTFBot):
        self.client = client
        self.ctfd_api = CTFd_API(client.config)

    async def cog_load(self):
        challenges = await self.ctfd_api.get_challenges()
        for challenge in challenges:
            self.challenge_categories.add(challenge["category"])

        self.challenge_categories.add("All")
        logger.success(
            f"Cached {len(self.challenge_categories)} challenge categories at startup."
        )

    async def cog_unload(self):
        await self.ctfd_api.close()

    @app_commands.command(name="scoreboard", description="Show the current scoreboard.")
    async def scoreboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        scoreboard = await self.ctfd_api.get_scoreboard()
        if not scoreboard:
            await interaction.followup.send("No scoreboard data found.", ephemeral=True)
            return

        # Sort by position (rank)
        scoreboard = sorted(scoreboard, key=lambda x: x["pos"])[:10]

        # Default = show full list view
        view = ViewScoreboard(scoreboard)
        embed = view.get_list_embed()

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="challenges", description="Get the challenges list.")
    @app_commands.describe(category="Filter challenges by category")
    async def challenges(self, interaction: discord.Interaction, category: str | None):
        await interaction.response.defer(thinking=True)

        challenges = await self.ctfd_api.get_challenges()

        if not challenges:
            await interaction.followup.send("No challenges found.", ephemeral=True)
            return

        if category:
            if category not in self.challenge_categories:
                await interaction.followup.send(
                    "Invalid category entered!", ephemeral=True
                )
                return

            if category != "All":
                challenges = filter(lambda ch: ch["category"] == category, challenges)

        categories: dict[str, list[Challenge]] = {}
        for ch in challenges:
            categories.setdefault(ch["category"], []).append(ch)

        description = ""
        for category, ch_list in categories.items():
            description += f"**{category}**\n"
            for ch in ch_list:
                name = ch["name"]
                solves = ch["solves"]
                points = ch["value"]
                description += f"- {name} *({points} points, {solves} solves)*\n"
            description += "\n"

        MAX_DESC_LEN = 4096
        chunks = textwrap.wrap(description, MAX_DESC_LEN, replace_whitespace=False)

        embeds: list[discord.Embed] = []
        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(
                title="🚩 Challenges List"
                if i == 1
                else f":books: Challenges List (Part {i})",
                description=chunk,
                color=discord.Color.teal(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embeds.append(embed)

        for embed in embeds:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @challenges.autocomplete("category")
    async def category_autocomplete(
        self, _interaction: discord.Interaction, current: str
    ):
        filtered = [
            app_commands.Choice(name=challenge, value=challenge)
            for challenge in self.challenge_categories
            if current.lower() in challenge.lower()
        ]
        return filtered[:25]


async def setup(client: ACUCySCTFBot):
    await client.add_cog(CtfD(client))
