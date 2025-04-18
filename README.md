# YouTube Playlist Exporter

Tired of videos disappearing from your YouTube playlists, without leaving you the option to know what was there before?

Fear not! For this CLI will have you covered

 ![alt text](memes/1.jpg)

This CLI allows exporting data about videos in your playlist to a local file, that can be used as a backup in case
videos from the playlist become private/get deleted.

## Installation

This CLI is published to [PyPI](https://pypi.org/project/youtube-playlist-exporter/) and can be installed with pip using:

`pip install youtube-playlist-exporter==0.1.0`

## Usage

1. Get a YouTube API Key. To do so, you can follow the instructions here: https://elfsight.com/help/how-to-get-youtube-api-key/
2. Retrieve the YouTube id of the playlist you want to create a backup for. This can be done in several ways. One of 
them is by navigating to the playlist's main YouTube page, and copying the text after "...list=" in the url
3. If you didn't do so already, install the CLI (see [installation](#installation))
4. Run the CLI using either the `ype` or `youtube-playlist-export` commands (full details on the CLI syntax are provided by running with the `--help` flag)
5. Several text files will be generated by the script in the output directory:
    1. **<PLAYLIST_NAME>-YoutubeBackupNew.txt**: contains the current updated lists of the titles of the provided YouTube playlist
    2. **<PLAYLIST_NAME>-YoutubeBackup.txt**: if a ...YoutubeBackupNew.txt file existed in the output directory before running the script, this file will be a backup for it (in case something went wrong with running the script etc.)
    3. **<PLAYLIST_NAME>-YoutubeBackupDiff.txt**: if a ...YoutubeBackupNew.txt file existed in the output directory before running the script, this file will contain the numbers of the videos whose title changed. This diff can handle new videos being added. However, if some videos from the old list were deleted, it won't take it into account properly
    4. **<PLAYLIST_NAME>-YoutubeBackupDiffOld.txt**: if a ...YoutubeBackupDiff.txt file existed in the output directory before running the script, this file will contain a backup for it

## TODOs

1. Allow exporting a CSV with additional details (video ID, channel that uploaded etc.) instead of just the video titles
2. Compare files based on video IDs?
3. Add additional backup mechanisms? GIT backup?