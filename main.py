import os

import typer
from typing_extensions import Annotated


def main(playlist_id: Annotated[str, typer.Argument(help="The YouTube id of the playlist to be backed up")],
         youtube_auth_key: Annotated[str, typer.Argument(
             help="The API key provided by YouTube")],
         output_dir: Annotated[str, typer.Argument(
             default_factory=os.getcwd,
             help="The script's output directory (must be an existing directory!) [default: current working directory]")],
         playlist_name: Annotated[str | None, typer.Argument(
             help="The name of the playlist to back-up. Only used for generating the names of the output files [default: the playlist id]")] = None,
         are_new_videos_last: Annotated[bool, typer.Argument(
             help="Whether new videos are added to the end of the playlist (in favorites' playlists they are added to the beginning, in other playlists to the end)")] = True):
    typer.echo(f"Input is: "
               f"playlist_id: {playlist_id}"
               f"youtube_auth_key: {youtube_auth_key}"
               f"output_dir: {output_dir}"
               f"playlist_name: {playlist_name}"
               f"are_new_videos_last: {are_new_videos_last}"
               )


if __name__ == "__main__":
    typer.run(main)
