import asyncio
import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import typedload
from aiohttp import ClientSession, ClientTimeout

from acucys_ctf.utils.environment import Config
from acucys_ctf.utils.errors import CTFdError


@dataclass
class Member:
    bracket_id: int | None
    bracket_name: str | None
    id: int
    name: str
    oauth_id: int | None
    score: int | None


@dataclass
class Score:
    pos: int
    account_id: int
    account_url: str
    account_type: Literal["team"]
    oauth_id: int | None
    name: str
    score: int
    bracket_id: int | None
    bracket_name: str | None
    members: list[Member]


@dataclass
class Challenge:
    id: int
    type: Literal["multiple_choice", "standard", "code"]
    name: str
    value: int
    solves: int
    solved_by_me: bool
    category: str
    tags: list[str]
    template: str
    script: str


@dataclass
class UserField:
    value: str | bool
    field_id: int
    description: str
    type: Literal["text", "boolean"]
    name: str


@dataclass
class User:
    affiliation: str | None
    team_id: int | None
    bracket_id: int | None
    oauth_id: int | None
    id: int
    fields: list[UserField]
    name: str
    website: str | None
    country: str | None

    def get_field(self, field_id: int) -> UserField | None:
        return next(filter(lambda field: field.field_id == field_id, self.fields), None)


@dataclass
class FullUser(User):
    change_password: bool
    language: str | None
    secret: str | None
    created: str  # javascript Date
    type: Literal["user", "admin"]
    hidden: bool
    verified: bool
    banned: bool
    place: str | None = field(default=None)
    score: int | None = field(default=None)


@dataclass
class RequestPagination:
    page: int
    next: int | None
    prev: int | None
    pages: int
    total: int


@dataclass
class Team:
    id: int
    banned: bool
    bracket_id: int | None
    fields: list[UserField]
    affiliation: str | None
    oauth_id: int | None
    secret: str | None
    hidden: bool
    name: str
    email: str | None
    created: str  # javascript Date
    country: str | None
    website: str | None
    captain_id: int


@dataclass
class FullTeam(Team):
    members: list[int]
    place: str
    score: int


@dataclass
class SolveStatistics:
    id: int
    name: str
    solves: int


@dataclass
class ChallengeSolve:
    account_id: int
    name: str
    date: str  # javascript Date
    account_url: str


@dataclass
class TeamSolveUser:
    name: str
    id: int


@dataclass
class TeamSolveChallenge:
    name: str
    category: str
    id: int
    value: int


@dataclass
class TeamSolveTeam:
    name: str
    id: int


@dataclass
class TeamSolve:
    user: TeamSolveUser
    ip: str
    challenge: TeamSolveChallenge
    team: TeamSolveTeam
    date: str  # javascript Date
    provided: str
    id: int
    challenge_id: int
    type: str


# typedload cannot deal with generics since all types must be fully qualified at runtime,
# so this is a workaround to allow for generics while having fully qualified types at runtime.


if TYPE_CHECKING:

    @dataclass
    class Request[T]:
        success: Literal[True]
        data: T
        meta: dict[str, Any] | None

        def get_pagination(self) -> RequestPagination | None: ...


def create_request_type[T](data_ty: type[T]) -> type[Request[T]]:
    @dataclass
    class Request:
        success: Literal[True]
        data: T
        meta: dict[str, Any] | None = field(default=None)

        def get_pagination(self) -> RequestPagination | None:
            if self.meta is not None and "pagination" in self.meta:
                return typedload.load(self.meta["pagination"], RequestPagination)
            return None

    Request.__annotations__["data"] = data_ty
    Request.__dataclass_fields__["data"].type = data_ty
    return Request  # type: ignore


ScoresRequest = create_request_type(list[Score])
ChallengesRequest = create_request_type(list[Challenge])
UsersRequest = create_request_type(list[User])
FullUserRequest = create_request_type(FullUser)
TeamsRequest = create_request_type(list[Team])
FullTeamRequest = create_request_type(FullTeam)
SolveStatisticsRequest = create_request_type(list[SolveStatistics])
ChallengeSolvesRequest = create_request_type(list[ChallengeSolve])
TeamSolvesRequest = create_request_type(list[TeamSolve])


class CTFd_API:
    session: ClientSession
    config: Config

    # Maps Discord user IDs to CTFd user IDs
    discord_id_cache: dict[int, int] = {}
    teams_cache_time: datetime.datetime = datetime.datetime(1970, 1, 1)
    teams_cache: list[Team] = []
    user_count = 0
    challenge_solves: dict[int, set[int]] = {}

    def __init__(self, config: Config):
        self.config = config
        self.session = ClientSession(
            f"{config.ctfd_instance_url}/api/v1/",
            timeout=ClientTimeout(total=config.api_timeout),
            headers={
                "Authorization": f"Token {config.ctfd_access_token}",
                "Content-Type": "application/json",
            },
        )

        asyncio.create_task(self._webhook_task())

    async def close(self):
        await self.session.close()

    async def _parse_request[T](
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE"],
        endpoint: str,
        ty: type[T],
        *,
        json: dict[str, Any] = {},
    ) -> T:
        response = await self.session.request(method, endpoint, json=json)
        if response.status != 200:
            raise CTFdError(f"Non-200 status code: {response.status} {response.reason}")

        value = await response.json()
        if "message" in value:
            raise CTFdError(f"CTFd error: {value['message']}")

        if "success" in value and not value["success"]:
            raise CTFdError("CTFd request failed.")

        return typedload.load(value, ty)

    async def _refresh_cache(self):
        # Pages are one-indexed with 50 users per page, and we always want to check for another user
        next_page = (self.user_count + 1) // 50 + 1
        while next_page is not None:
            page = await self._parse_request(
                "GET", f"users?page={next_page}", UsersRequest
            )

            pagination = page.get_pagination()
            if pagination is None:
                raise CTFdError("Users endpoint was not paginated.")

            for user in page.data:
                discord_id = user.get_field(self.config.discord_id_field)
                if discord_id is None:
                    continue

                self.discord_id_cache[int(discord_id.value)] = user.id

            next_page = pagination.next

    async def get_scoreboard(self) -> list[Score]:
        return (await self._parse_request("GET", "scoreboard", ScoresRequest)).data

    async def get_challenges(self) -> list[Challenge]:
        return (await self._parse_request("GET", "challenges", ChallengesRequest)).data

    async def get_user(self, user_id: int) -> FullUser:
        return (
            await self._parse_request("GET", f"users/{user_id}", FullUserRequest)
        ).data

    async def get_user_from_discord(self, discord_id: int) -> FullUser | None:
        user_id = self.discord_id_cache.get(discord_id)

        if user_id is None:
            await self._refresh_cache()

            user_id = self.discord_id_cache.get(discord_id)
            if user_id is None:
                return None

        return await self.get_user(user_id)

    async def get_full_team(self, team_id: int) -> FullTeam:
        return (
            await self._parse_request("GET", f"teams/{team_id}", FullTeamRequest)
        ).data

    async def get_team_solves(self, team_id: int) -> list[TeamSolve]:
        return (
            await self._parse_request(
                "GET", f"teams/{team_id}/solves", TeamSolvesRequest
            )
        ).data

    async def get_teams(self, *, invalidate_cache: bool = False) -> list[Team]:
        if (
            datetime.datetime.now() - self.teams_cache_time
        ).seconds < self.config.cache_timeout and not invalidate_cache:
            return self.teams_cache

        teams: list[Team] = []

        next_page = 1
        while next_page is not None:
            page = await self._parse_request("GET", "teams", TeamsRequest)

            pagination = page.get_pagination()
            if pagination is None:
                raise CTFdError("Teams endpoint was not paginated.")

            teams += page.data
            next_page = pagination.next

        self.teams_cache = teams
        self.teams_cache_time = datetime.datetime.now()
        return teams

    async def register_user(
        self, name: str, email: str, password: str, discord_id: int
    ) -> FullUser:
        user = await self._parse_request(
            "POST",
            "users",
            FullUserRequest,
            json={
                "name": name,
                "email": email,
                "password": password,
                "change_password": True,
                "fields": [
                    {
                        "value": str(discord_id),
                        "field_id": self.config.discord_id_field,
                        "description": "",
                        "type": "text",
                        "name": "Discord UserID",
                    }
                ],
            },
        )

        self.discord_id_cache[discord_id] = user.data.id
        return user.data

    async def _webhook_task(self):
        new_solves: set[tuple[Any, str]] = set()
        is_init = len(self.challenge_solves) == 0
        total_solves = await self._parse_request(
            "GET", "statistics/challenges/solves", SolveStatisticsRequest
        )

        for challenge in total_solves.data:
            stored_solves = self.challenge_solves.setdefault(challenge.id, set())
            if len(stored_solves) == challenge.solves:
                continue

            solves = await self._parse_request(
                "GET", f"challenges/{challenge.id}/solves", ChallengeSolvesRequest
            )
            for solve in solves.data:
                if solve.account_id in stored_solves:
                    continue

                stored_solves.add(solve.account_id)
                if is_init:
                    continue

                team_solves = await self.get_team_solves(solve.account_id)
                solve = next(
                    filter(
                        lambda solve: solve.challenge_id == challenge.id, team_solves
                    )
                )

                user = await self.get_user(solve.user.id)
                discord_id = user.get_field(self.config.discord_id_field)
                if discord_id is None:
                    continue

                new_solves.add((discord_id.value, challenge.name))

        if len(new_solves) != 0:
            async with ClientSession(
                timeout=ClientTimeout(total=self.config.api_timeout)
            ) as session:
                await session.post(
                    self.config.webhook_url,
                    json={
                        "content": "\n".join(
                            [
                                f"<@{solve[0]}> just solved {solve[1]}!"
                                for solve in new_solves
                            ]
                        )
                    },
                )

        await asyncio.sleep(self.config.webhook_frequency)
        asyncio.create_task(self._webhook_task())
