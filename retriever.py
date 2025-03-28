import asyncio
import typing

import typer
from aiohttp import ClientSession

PLAYLIST_API = "https://www.googleapis.com/youtube/v3/playlistItems/"


class PlaylistDataRetriever:
    def __init__(self, session: ClientSession, playlist_id: str, auth_key: str):
        self._session: ClientSession = session
        self._playlist_id: str = playlist_id
        self._auth_key: str = auth_key
        self._next_page: str = ""
        self._titles: list[str] = []

    async def retrieve(self) -> list[str]:
        while True:
            resp = await self._send_bulk_request()
            self._next_page = resp.get("nextPageToken")
            if not self._next_page:
                typer.echo()
                return self._titles

            self._titles += [item["snippet"]["title"] for item in resp["items"]]
            await asyncio.sleep(0.2) # Without sleep sometimes irregularities in the API response pop up
            typer.echo(f"\rRetrieved data about {len(self._titles)} videos", nl=False)

    async def _send_bulk_request(self) -> dict[str, typing.Any]:
        req_url = self._get_req_url()
        async with self._session.get(req_url) as response:
            if response.status != 200:
                raise Exception(f"Received non 200 code from YouTube API: {response.status}")

            return await response.json()

    def _get_req_url(self):
        next_page_part = "" if self._next_page == "" else f"&pageToken{self._next_page}"
        return f"{PLAYLIST_API}?part=snippet&maxResults=50&playlistId={self._playlist_id}&key={self._auth_key}{next_page_part}"
