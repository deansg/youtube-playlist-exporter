import asyncio

import typer
from aiohttp import ClientSession
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.apimodels import PlaylistItem, APIResponse
from app.options import Options

PLAYLIST_API = "https://www.googleapis.com/youtube/v3/playlistItems/"

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


class PlaylistDataRetriever:
    def __init__(self, session: ClientSession, options: Options):
        self._session: ClientSession = session
        self._options: Options = options
        self._next_page: str = ""
        self._items: list[PlaylistItem] = []
        self._credentials: Credentials | None = self._authenticate_youtube() if options.private_playlist else None

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

    def _authenticate_youtube(self) -> Credentials:
        flow = InstalledAppFlow.from_client_secrets_file(self._options.secret_file, SCOPES)
        return flow.run_local_server(port=0)

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
        auth_section = f"access_token={self._credentials.token}" if self._options.private_playlist else f"key={self._options.youtube_auth_key}"
        return f"{PLAYLIST_API}?part=snippet&maxResults=50&playlistId={self._options.playlist_id}&{auth_section}{next_page_part}"
