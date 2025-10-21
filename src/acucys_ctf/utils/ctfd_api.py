from dataclasses import dataclass
from typing import Literal

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
    score: int


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


class CTFd_API:
    session: ClientSession

    def __init__(self, config: Config):
        self.session = ClientSession(
            f"{config.ctfd_instance_url}/api/v1/",
            timeout=ClientTimeout(total=5),
            headers={
                "Authorization": f"Token {config.ctfd_access_token}",
                "Content-Type": "application/json",
            },
        )

    async def close(self):
        await self.session.close()

    async def _get_data[T](self, endpoint: str, ty: type[T]) -> T:
        request = await self.session.get(endpoint)
        if request.status != 200:
            raise CTFdError(f"Non-200 status code: {request.status} {request.reason}")

        value = await request.json()
        if "message" in value:
            raise CTFdError(f"CTFd error: {value['message']}")

        if "success" in value and not value["success"]:
            raise CTFdError("CTFd request failed.")

        if "data" not in value:
            raise CTFdError("Unexpected response.")

        return typedload.load(value["data"], ty)

    async def get_scoreboard(self):
        return await self._get_data("scoreboard", list[Score])

    async def get_challenges(self):
        return await self._get_data("challenges", list[Challenge])
