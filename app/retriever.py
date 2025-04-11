import asyncio

import typer
from aiohttp import ClientSession

from app.apimodels import PlaylistItem
from app.apimodels import APIResponse

PLAYLIST_API = "https://www.googleapis.com/youtube/v3/playlistItems/"


class PlaylistDataRetriever:
    def __init__(self, session: ClientSession, playlist_id: str, auth_key: str):
        self._session: ClientSession = session
        self._playlist_id: str = playlist_id
        self._auth_key: str = auth_key
        self._next_page: str = ""
        self._items: list[PlaylistItem] = []

    async def retrieve(self) -> list[PlaylistItem]:
        while True:
            resp = await self._send_bulk_request()
            self._next_page = resp.next_page_token
            self._items += resp.items
            typer.echo(f"\rRetrieved data about {len(self._items)} videos", nl=False)
            if not self._next_page:
                typer.echo()
                return self._items
            await asyncio.sleep(0.2)  # Without sleep sometimes irregularities in the API response pop up

    async def _send_bulk_request(self) -> APIResponse:
        req_url = self._get_req_url()
        async with self._session.get(req_url) as response:
            if response.status != 200:
                raise Exception(f"Received non 200 code from YouTube API: {response.status}")

            raw_resp = await response.json()
            # noinspection PyUnresolvedReferences
            return APIResponse.from_dict(raw_resp)

    def _get_req_url(self):
        next_page_part = "" if self._next_page == "" else f"&pageToken={self._next_page}"
        return f"{PLAYLIST_API}?part=snippet&maxResults=50&playlistId={self._playlist_id}&key={self._auth_key}{next_page_part}"
