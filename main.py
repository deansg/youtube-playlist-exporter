import asyncio
import os

import aiohttp
import typer
from typing_extensions import Annotated

from exporter import YouTubePlaylistExporter
from options import Options


def main(playlist_id: Annotated[str, typer.Argument(help="The YouTube id of the playlist to export")],
         youtube_auth_key: Annotated[str, typer.Argument(
             help="The API key provided by YouTube",
             envvar="AUTH_KEY")],
         output_dir: Annotated[str, typer.Argument(
             default_factory=os.getcwd,
             help="The script's output directory (must be an existing directory!) [default: current working directory]")],
         playlist_name: Annotated[str | None, typer.Argument(
             help="The name of the playlist to back-up. Only used for generating the names of the output files [default: the playlist id]")] = None,
         are_new_videos_last: Annotated[bool, typer.Argument(
             help="Whether new videos are added to the end of the playlist (in favorites' playlists they are added to the beginning, in other playlists to the end)")] = True):
    asyncio.run(_run(Options(playlist_id=playlist_id,
                             youtube_auth_key=youtube_auth_key,
                             output_dir=output_dir,
                             playlist_name=playlist_name,
                             are_new_videos_last=are_new_videos_last)))

async def _run(options: Options):
    async with aiohttp.ClientSession() as session:
        await YouTubePlaylistExporter(session).export_playlist(options)


if __name__ == "__main__":
    typer.run(main)
