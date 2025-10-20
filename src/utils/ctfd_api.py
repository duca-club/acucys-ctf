# import os
import aiohttp
import asyncio

from bot.utils.environment import ENV_CTFD_INSTANCE_URL
from bot.utils.environment import ENV_CTFD_ACCESS_TOKEN

class CTFd_API:

    @staticmethod
    async def _get_json(url: str, headers: dict, error_context: str = "CTFd API request"):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=5) as response:  # type: ignore
                    if response.status != 200:
                        raise RuntimeError(f"{error_context} returned HTTP {response.status}")
                    return await response.json()

        except asyncio.TimeoutError:
            raise TimeoutError(f"{error_context} timed out.")
        except aiohttp.ClientError as e:
            raise ConnectionError(f"{error_context} connection error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during {error_context}: {e}")

    @staticmethod
    async def get_scoreboard():
        url = f"{ENV_CTFD_INSTANCE_URL}/scoreboard"
        headers = {
            "Content-Type": "application/json"
        }

        data = await CTFd_API._get_json(url, headers, "Fetching scoreboard")
        return data.get("data", [])
            
    @staticmethod
    async def get_challenge_categories():
        url = f"{ENV_CTFD_INSTANCE_URL}/challenges"
        headers = {
            "Authorization": f"Token {ENV_CTFD_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        data = await CTFd_API._get_json(url, headers, "Fetching challenge categories")

        if not data.get("success", False):
            raise RuntimeError("CTFd API returned an unsuccessful response!")

        all_items = data.get("data", [])
        categories = list({item.get("category") for item in all_items if item.get("category")})
        return categories

    @staticmethod
    async def get_challenges():
        url = f"{ENV_CTFD_INSTANCE_URL}/challenges"
        headers = {
            "Authorization": f"Token {ENV_CTFD_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        data = await CTFd_API._get_json(url, headers, "Fetching challenges")

        if not data.get("success", False):
            raise RuntimeError("CTFd API returned an unsuccessful response!")

        return data.get("data", [])
