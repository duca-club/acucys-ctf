# import os
import aiohttp
import asyncio

from bot.utils.environment import ENV_CTFD_INSTANCE_URL
from bot.utils.environment import ENV_CTFD_ACCESS_TOKEN

class CTFd_API:

    @staticmethod
    async def get_scoreboard():
        url = f"{ENV_CTFD_INSTANCE_URL}/scoreboard"
        headers = {
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=5) as response: # type: ignore
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    else:
                        raise RuntimeError(f"CTFd API returned HTTP {response.status}")
            except asyncio.TimeoutError:
                raise TimeoutError("CTFd API request timed out.")
            except aiohttp.ClientError as e:
                raise ConnectionError(f"CTFd API connection error: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error fetching scoreboard: {e}")

    @staticmethod
    async def get_challenges():
        url = f"{ENV_CTFD_INSTANCE_URL}/challenges"
        headers = {
            "Authorization": f"Token {ENV_CTFD_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=5) as response: # type: ignore
                    if response.status == 200:
                        data = await response.json()
                        print(data)
                        if data.get("success", False):
                            return data.get("data", [])
                        else:
                            raise RuntimeError("CTFd API returned an unsuccessfull response!")
                    else:
                        raise RuntimeError(f"CTFd API returned HTTP {response.status}.")
            except asyncio.TimeoutError:
                raise TimeoutError("CTFd API request timed out.")
            except aiohttp.ClientError as e:
                raise ConnectionError(f"CTFd API connection error: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error fetching scoreboard: {e}")
