from dataclasses import dataclass


@dataclass
class Options:
    playlist_id: str
    youtube_auth_key: str
    output_dir: str
    playlist_name: str
    are_new_videos_last: bool
