from datetime import datetime

import typer


def log(msg: str):
    typer.echo(f"{datetime.now().isoformat()}: {msg}")

def get_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"
