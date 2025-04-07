from datetime import datetime

import typer


def log(msg: str):
    typer.echo(f"{datetime.now().isoformat()}: {msg}")
