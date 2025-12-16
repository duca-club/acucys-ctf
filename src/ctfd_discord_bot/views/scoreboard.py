import datetime
import typing

import discord

from ctfd_discord_bot.utils.ctfd_api import Score


def get_team_embed(team: Score) -> discord.Embed:
    desc_prefix = title_prefix = ""
    if team.pos is not None:
        title_prefix = f"🚩 {team.pos}. "
        desc_prefix = f"**Rank**: *{team.pos}*\n"

    embed = discord.Embed(
        title=title_prefix + f"Team *{team.name}*",
        color=discord.Color.gold(),
        description=desc_prefix + f"**Total Score**: *{team.score}*",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )

    if team.members:
        member_lines = "\n".join(
            f"• **{member.name}**: {member.score} pts" for member in team.members
        )
        embed.add_field(name="Members", value=member_lines, inline=False)
    else:
        embed.add_field(name="Members", value="No members found.", inline=False)

    return embed


class Scoreboard(discord.ui.View):
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
                f"{entry.pos}.**{entry.name}**: *({entry.score} points)*"
            )

        embed.description = "\n".join(description_lines)
        return embed

    def get_team_embed(self):
        """Embed showing a single team."""
        entry = self.scoreboard[self.current_index]
        embed = get_team_embed(entry)
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
                embed=self.get_team_embed(),
                view=self,
            )
