import asyncio
import os

import aiohttp
import typer
from typing_extensions import Annotated

from app.exportmanager import YouTubePlaylistExportManager
from app.options import Options

app = typer.Typer()


@app.command()
def main(playlist_id: Annotated[str, typer.Option(help="The YouTube id of the playlist to export")],
         youtube_auth_key: Annotated[str, typer.Option(
             help="The API key provided by YouTube",
             envvar="AUTH_KEY")],
         output_dir: Annotated[str, typer.Option(
             default_factory=os.getcwd,
             help="The script's output directory (must be an existing directory!) [default: current working directory]")],
         playlist_name: Annotated[str | None, typer.Option(
             help="The name of the playlist to back-up. Only used for generating the names of the output files [default: the playlist id]")] = None,
         new_videos_first: Annotated[bool, typer.Option(
             help="Whether new videos are added to the beginning of the playlist (in favorites' playlists they are added to the beginning, in other playlists to the end)")] = False,
         csv_output: Annotated[bool, typer.Option(
             help="Experimental")] = False,
         ):
    asyncio.run(_run(Options(playlist_id=playlist_id,
                             youtube_auth_key=youtube_auth_key,
                             output_dir=output_dir,
                             playlist_name=playlist_name,
                             are_new_videos_last=not new_videos_first,
                             csv_output=csv_output,
                             )))


async def _run(options: Options):
    async with aiohttp.ClientSession() as session:
        await YouTubePlaylistExportManager(session, options).export_playlist()


if __name__ == "__main__":
    app()
