import datetime
import random
import re
import string
import textwrap

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from ctfd_discord_bot import CTFdBot
from ctfd_discord_bot.utils.ctfd_api import Challenge, CTFd_API, Member, Score
from ctfd_discord_bot.views.scoreboard import Scoreboard, get_team_embed

EMAIL_REGEX = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
MAX_DESC_LEN = 4096
REGISTER_COOLDOWN = 60
REGULAR_COOLDOWN = 3


class CtfD(commands.Cog):
    challenge_categories: dict[str, dict[int, tuple[str, int]]] = {}
    total_challenges: int = 0
    current_registrations: set[int] = set()

    def __init__(self, client: CTFdBot):
        self.client = client
        self.ctfd_api = CTFd_API(client.config)

    async def cog_load(self):
        challenges = await self.ctfd_api.get_challenges()
        for challenge in challenges:
            self.total_challenges += 1
            self.challenge_categories.setdefault(challenge.category, {})[
                challenge.id
            ] = (challenge.name, challenge.value)

        logger.success(
            f"Cached {len(self.challenge_categories)} challenge categories at startup."
        )

    async def cog_unload(self):
        await self.ctfd_api.close()

    @app_commands.command(name="scoreboard", description="Show the current scoreboard.")
    @app_commands.checks.cooldown(1, REGULAR_COOLDOWN)
    async def scoreboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        scoreboard = await self.ctfd_api.get_scoreboard()
        if not scoreboard:
            await interaction.followup.send("No scoreboard data found.", ephemeral=True)
            return

        # Sort by position (rank)
        scoreboard = sorted(
            scoreboard, key=lambda x: x.pos if x.pos is not None else 1e9
        )[:10]

        # Default = show full list view
        view = Scoreboard(scoreboard)
        embed = view.get_list_embed()

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="challenges", description="Get the challenges list.")
    @app_commands.describe(category="Filter challenges by category")
    @app_commands.checks.cooldown(1, REGULAR_COOLDOWN)
    async def challenges(self, interaction: discord.Interaction, category: str | None):
        if category == "All":
            category = None

        if category is not None and category not in self.challenge_categories:
            await interaction.response.send_message(
                "Invalid category entered!", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        challenges = await self.ctfd_api.get_challenges()

        if len(challenges) == 0:
            await interaction.followup.send("No challenges found.", ephemeral=True)
            return

        if category is not None:
            challenges = filter(lambda ch: ch.category == category, challenges)

        categories: dict[str, list[Challenge]] = {}
        for ch in challenges:
            categories.setdefault(ch.category, []).append(ch)

        description = ""
        for category, ch_list in categories.items():
            description += f"**{category}**\n"
            for ch in ch_list:
                description += (
                    f"- {ch.name} *({ch.value} points, {ch.solves} solves)*\n"
                )
            description += "\n"

        chunks = textwrap.wrap(description, MAX_DESC_LEN, replace_whitespace=False)

        embeds: list[discord.Embed] = []
        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(
                title="🚩 Challenge List"
                if i == 1
                else f":books: Challenge List (Part {i})",
                description=chunk,
                color=discord.Color.teal(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embeds.append(embed)

        for embed in embeds:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="progress", description="Get the solve progress of your team."
    )
    @app_commands.describe(category="Filter solves by challenge category")
    @app_commands.checks.cooldown(1, REGULAR_COOLDOWN)
    async def progress(self, interaction: discord.Interaction, category: str | None):
        if category == "All":
            category = None

        if category is not None and category not in self.challenge_categories:
            await interaction.response.send_message(
                "Invalid category entered!", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        user = await self.ctfd_api.get_user_from_discord(interaction.user.id)
        if user is None:
            await interaction.followup.send(
                "You do not have an account.", ephemeral=True
            )
            return

        if user.team_id is None:
            await interaction.followup.send("You are not in a team.", ephemeral=True)
            return

        total = self.total_challenges
        categories: dict[str, dict[int, list[str | int | None]]] = {
            category: {
                challenge_id: [challenge[0], challenge[1], None]
                for challenge_id, challenge in challenges.items()
            }
            for category, challenges in self.challenge_categories.items()
        }

        solves = await self.ctfd_api.get_team_solves(user.team_id)
        solves_num = len(solves)
        for solve in solves:
            categories[solve.challenge.category][solve.challenge_id][2] = (
                solve.user.name
            )

        if category is not None:
            challenges = categories[category]
            total = len(challenges)
            solves_num = sum(
                1
                for _ in filter(
                    lambda solve: solve.challenge.category == category, solves
                )
            )
            categories = {category: challenges}

        description = f"**Progress:** {solves_num}/{total}\n"
        for category, challenges in categories.items():
            description += f"**{category}**\n"
            for challenge in challenges.values():
                description += f"- {challenge[0]} *({challenge[1]} points)* {'is unsolved.' if challenge[2] is None else f'was solved by {challenge[2]}'}\n"
            description += "\n"

        chunks = textwrap.wrap(description, MAX_DESC_LEN, replace_whitespace=False)

        embeds: list[discord.Embed] = []
        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(
                title="🚩 Team Progress"
                if i == 1
                else f":books: Team Progress (Part {i})",
                description=chunk,
                color=discord.Color.teal(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embeds.append(embed)

        for embed in embeds:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @challenges.autocomplete("category")
    @progress.autocomplete("category")
    async def category_autocomplete(
        self, _interaction: discord.Interaction, current: str
    ):
        filtered = [
            app_commands.Choice(name=category, value=category)
            for category in self.challenge_categories
            if current.lower() in category.lower()
        ]

        if current.lower() in "all":
            filtered.append(app_commands.Choice(name="All", value="All"))

        return filtered[:25]

    @app_commands.command(
        name="team", description="Get information about a specific team."
    )
    @app_commands.describe(
        team="The team name to check. Leave blank for your own team."
    )
    @app_commands.checks.cooldown(1, REGULAR_COOLDOWN)
    async def team(self, interaction: discord.Interaction, team: str | None):
        await interaction.response.defer(thinking=True, ephemeral=True)

        team_id: int
        if team is None:
            user = await self.ctfd_api.get_user_from_discord(interaction.user.id)
            if user is None:
                await interaction.followup.send(
                    "You do not have an account.", ephemeral=True
                )
                return

            if user.team_id is None:
                await interaction.followup.send(
                    "You are not in a team.", ephemeral=True
                )
                return

            team_id = user.team_id
        else:
            teams = await self.ctfd_api.get_teams(invalidate_cache=True)
            try:
                team_id = next(filter(lambda t: t.name == team, teams)).id
            except StopIteration:
                await interaction.followup.send(
                    f"There is no team with the name `{team}`.", ephemeral=True
                )
                return

        full_team = await self.ctfd_api.get_full_team(team_id)
        members: list[Member] = []
        for member_id in full_team.members:
            full_user = await self.ctfd_api.get_user(member_id)
            members.append(
                Member(
                    bracket_id=full_user.bracket_id,
                    bracket_name=None,
                    id=member_id,
                    name=full_user.name,
                    oauth_id=full_user.oauth_id,
                    score=full_user.score,
                )
            )

        pos = None
        if full_team.place is not None:
            pos = re.sub("[^0-9]", "", full_team.place)
            if pos == "":
                pos = None
            else:
                pos = int(pos)

        await interaction.followup.send(
            ephemeral=True,
            embed=get_team_embed(
                Score(
                    pos=pos,
                    account_id=full_team.id,
                    account_url=f"teams/{full_team.id}",
                    account_type="team",
                    oauth_id=full_team.oauth_id,
                    name=full_team.name,
                    score=full_team.score,
                    bracket_id=full_team.bracket_id,
                    bracket_name=None,
                    members=members,
                )
            ),
        )

    @team.autocomplete("team")
    async def team_autocomplete(self, _interaction: discord.Interaction, current: str):
        filtered = [
            app_commands.Choice(name=team.name, value=team.name)
            for team in await self.ctfd_api.get_teams()
            if current.lower() in team.name.lower()
        ]
        return filtered[:25]

    @app_commands.command(name="register", description="Register for the CTF.")
    @app_commands.checks.cooldown(1, REGISTER_COOLDOWN)
    async def register_user(self, interaction: discord.Interaction):
        if interaction.user.id in self.current_registrations:
            await interaction.response.send_message(
                "You already have an ongoing registration, check your DMs.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        user = await self.ctfd_api.get_user_from_discord(interaction.user.id)
        if user is not None:
            await interaction.followup.send(
                "You already have an account.", ephemeral=True
            )
            return

        await interaction.followup.send(
            "Check your DMs to continue the account creation process.", ephemeral=True
        )

        self.current_registrations.add(interaction.user.id)
        channel = await interaction.user.create_dm()

        def message_check(msg: discord.Message) -> bool:
            return msg.channel.id == channel.id and msg.author.id == interaction.user.id

        try:
            await channel.send(
                embed=discord.Embed(
                    title=f"{self.client.config.event_name} Account Creation",
                    color=discord.Color.teal(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    description=f"""
Welcome to the {self.client.config.event_name} Account Creation.
To continue, please enter your preferred email address.
""",
                )
            )
        except discord.Forbidden as exc:
            # 50007 is the error code for being unable to send a message to a user
            if exc.code != 50007:
                raise exc

            await interaction.followup.send(
                "You do not have DMs enabled. Please enable them to register or contact an admin.",
                ephemeral=True,
            )
            return

        email: str = ""
        for i in range(5):
            try:
                msg = await self.client.wait_for(
                    "message",
                    check=message_check,
                    timeout=self.client.config.register_timeout,
                )
            except TimeoutError:
                return await self.register_timeout(interaction.user.id, channel)

            if re.search(EMAIL_REGEX, msg.content) is not None:
                email = msg.content
                break

            if i == 4:
                self.current_registrations.remove(interaction.user.id)
                await channel.send(
                    embed=discord.Embed(
                        title=f"{self.client.config.event_name} Account Creation",
                        color=discord.Color.red(),
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        description="""
You entered an invalid email address too many times.
Please try again later.
""",
                    )
                )
                return

            await channel.send(
                embed=discord.Embed(
                    title=f"{self.client.config.event_name} Account Creation",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    description="""
You entered an invalid email address.
Please try again.
""",
                )
            )

        await channel.send(
            embed=discord.Embed(
                title=f"{self.client.config.event_name} Account Creation",
                color=discord.Color.teal(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                description="""
Thank you. Please enter your preferred username.
""",
            )
        )

        try:
            msg = await self.client.wait_for(
                "message",
                check=message_check,
                timeout=self.client.config.register_timeout,
            )
        except TimeoutError:
            return await self.register_timeout(interaction.user.id, channel)

        # Doesn't have to be cryptographically secure. Is only a temporary password used until they login.
        password = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        user = await self.ctfd_api.register_user(
            msg.content, email, password, interaction.user.id
        )

        await channel.send(
            embed=discord.Embed(
                title=f"{self.client.config.event_name} Account Creation",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                description=f"""
Thank you. Your account has been created successfully!
Your temporary password is `{password}`, and you will be prompted to change it upon login.
You can change other information such as your website, and join a team once logged in.
You can [login here.]({self.client.config.ctfd_instance_url}/login)
""",
            )
        )

        self.current_registrations.remove(interaction.user.id)

    async def register_timeout(self, id: int, channel: discord.DMChannel):
        self.current_registrations.remove(id)
        await channel.send(
            embed=discord.Embed(
                title=f"{self.client.config.event_name} Account Creation",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                description="""
Account creation timed out.
""",
            )
        )


async def setup(client: CTFdBot):
    await client.add_cog(CtfD(client))
