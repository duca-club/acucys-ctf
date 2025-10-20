import datetime
import discord
import textwrap
from discord import app_commands
from discord.ext import commands
from bot.utils.ctfd_api import CTFd_API
from loguru import logger
from bot.utils.environment import is_dev_mode

class ViewScoreboard(discord.ui.View):
    def __init__(self, scoreboard, current_index=0):
        super().__init__(timeout=180)
        self.scoreboard = scoreboard
        self.current_index = current_index
        self.showing_list = True
        self.update_buttons()

    def update_buttons(self):
        """Enable/disable navigation depending on mode and index."""
        self.left.disabled = self.showing_list or self.current_index <= 0
        self.right.disabled = self.showing_list or self.current_index >= len(self.scoreboard) - 1
        self.list.label = "📋 View Team Details" if self.showing_list else "📋 Back to Team List"

    def get_list_embed(self):
        """Embed showing all teams in the description."""
        embed = discord.Embed(
            title=":trophy: Scoreboard: All Teams",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        # Build a formatted description string
        description_lines = []
        for entry in self.scoreboard:
            name = entry.get("name", "Unknown")
            score = entry.get("score", 0)
            pos = entry.get("pos", 0)
            description_lines.append(f"{pos}.**{name}**: *({score} points)*")

        embed.description = "\n".join(description_lines)
        return embed


    def get_team_embed(self):
        """Embed showing a single team."""
        entry = self.scoreboard[self.current_index]
        name = entry.get("name", "Unknown")
        score = entry.get("score", 0)
        rank = entry.get("pos", "?")
        members = entry.get("members", [])

        embed = discord.Embed(
            title=f"🚩 {rank}. Team *{name}*",
            color=discord.Color.gold(),
            description=f"**Rank**: *{rank}*\n**Total Score**: *{score}*",
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        if members:
            member_lines = "\n".join(
                f"• **{m.get('name', 'Unknown')}**: {m.get('score', 0)} pts"
                for m in members
            )
            embed.add_field(name="Members", value=member_lines, inline=False)
        else:
            embed.add_field(name="Members", value="No members found.", inline=False)

        embed.set_footer(text=f"Team {self.current_index + 1} of {len(self.scoreboard)}")
        return embed

    # ⬅️
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.showing_list and self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_team_embed(), view=self)

    # 📋
    @discord.ui.button(label="📋 View Team Details", style=discord.ButtonStyle.primary)
    async def list(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle between list and single team view."""
        self.showing_list = not self.showing_list
        self.update_buttons()
        embed = self.get_list_embed() if self.showing_list else self.get_team_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    # ➡️
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.showing_list and self.current_index < len(self.scoreboard) - 1:
            self.current_index += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_team_embed(), view=self)


class CtfD(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.challenges_options = []
    
    async def cog_load(self):
        try:
            self.challenges_options = await CTFd_API.get_challenge_categories()
            self.challenges_options.append("All")
            logger.success(f"Cached {len(self.challenges_options)} challenge categories at startup.")
        except Exception as e:
            logger.error(f"Failed to load challenge categories at startup: {e}")
            self.challenges_options = []

    @app_commands.command(name="scoreboard", description="Show the current scoreboard.")
    async def scoreboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            scoreboard = await CTFd_API.get_scoreboard()
            if not scoreboard:
                await interaction.followup.send("No scoreboard data found.", ephemeral=True)
                return

            # Sort by position (rank)
            scoreboard = sorted(scoreboard, key=lambda x: x.get("pos", 9999))[:10]

            # Default = show full list view
            view = ViewScoreboard(scoreboard)
            embed = view.get_list_embed()

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            if is_dev_mode():
                await interaction.followup.send(f"An unexpected error occurred while fetching the scoreboard.\n```{e}```", ephemeral=True)
            else:
                await interaction.followup.send(f"An unexpected error occurred while fetching the scoreboard.", ephemeral=True)

    @app_commands.command(name="challenges", description="Get the challenges list.")
    @app_commands.describe(category="Filter challenges by category")
    async def challenges(self, interaction: discord.Interaction, category: str):
        await interaction.response.defer(thinking=True)

        try:
            challenges = await CTFd_API.get_challenges()

            if not challenges:
                await interaction.followup.send("No challenges found.", ephemeral=True)
                
            if category:
                if not(category in self.challenges_options):
                    await interaction.followup.send("Invalid catgeory entered!", ephemeral=True)
                    return
                
                if not category == "All":
                    challenges = [ch for ch in challenges if ch.get("category") == category]

            categories = {}
            for ch in challenges:
                cat = ch.get("category", "Uncategorized")
                categories.setdefault(cat, []).append(ch)
            
            description = ""
            for category, ch_list in categories.items():
                description += f"**{category}**\n"
                for ch in ch_list:
                    name = ch.get("name", "Unknown")
                    solves = ch.get("solves", 0)
                    points = ch.get("value", 0)
                    description += f"- {name} *({points} points, {solves} solves)*\n"
                description += "\n"

            MAX_DESC_LEN = 4096
            chunks = textwrap.wrap(description, MAX_DESC_LEN, replace_whitespace=False)

            embeds = []
            for i, chunk in enumerate(chunks, start=1):
                embed = discord.Embed(
                    title="🚩 Challenges List" if i == 1 else f":books: Challenges List (Part {i})",
                    description=chunk,
                    color=discord.Color.teal(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embeds.append(embed)
            
            for embed in embeds:
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            if is_dev_mode():
                await interaction.followup.send(f"An unexpected error occurred while fetching the challenges.\n```{e}```", ephemeral=True)
            else:
                await interaction.followup.send(f"An unexpected error occurred while fetching the challenges.", ephemeral=True)

    @challenges.autocomplete("category")
    async def category_autocomplete(self, interaction: discord.Interaction, current: str):
        if not self.challenges_options:
            return []
        filtered = [
            app_commands.Choice(name=c, value=c)
            for c in self.challenges_options
            if current.lower() in c.lower()
        ]
        return filtered[:25]

async def setup(client: commands.Bot):
    await client.add_cog(CtfD(client))
