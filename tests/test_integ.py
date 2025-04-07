import os.path
import tempfile

import pytest
from aioresponses import aioresponses
from click.testing import Result
from typer.testing import CliRunner

from app.main import app

runner = CliRunner()


@pytest.fixture()
def playlist_id() -> str:
    return "TEST_ID"


@pytest.fixture()
def playlist_name() -> str:
    return "TEST_PLAYLIST_NAME"


@pytest.fixture()
def auth_key() -> str:
    return "TEST_AUTH_KEY"


@pytest.fixture
def m():
    with aioresponses() as m:
        yield m


@pytest.fixture()
def mock_api_calls(playlist_id: str, playlist_name: str, auth_key: str, m):
    resp1 = _read_test_resource("resp_1.json")
    resp2 = _read_test_resource("resp_2.json")
    resp3 = _read_test_resource("resp_3.json")
    m.get("https://www.googleapis.com/youtube/v3/playlistItems/?part=snippet&maxResults=50&"
          f"playlistId={playlist_id}&key={auth_key}",
          body=resp1)
    m.get(f"https://www.googleapis.com/youtube/v3/playlistItems/?part=snippet&maxResults=50&"
          f"playlistId={playlist_id}&key={auth_key}&pageToken=EAAaHlBUOkNESWlFRFF4UXpnMk1UYzBNME00T1RKR05ETQ",
          body=resp2)
    m.get(f"https://www.googleapis.com/youtube/v3/playlistItems/?part=snippet&maxResults=50&"
          f"playlistId={playlist_id}&key={auth_key}&pageToken=EAAaH1BUOkNNWUtJaEJGTWprek9FRkZRamMxT0RBNU1rTkU",
          body=resp3)


@pytest.fixture()
def tempdir():
    with tempfile.TemporaryDirectory() as tempdir:
        yield tempdir


def test_empty_directory(tempdir: str, mock_api_calls, playlist_id: str, playlist_name: str, auth_key: str):
    diff_file = f"{playlist_name}YoutubeBackupDiff.txt"
    data_file = f"{playlist_name}YoutubeBackupNew.txt"

    result = _run_cli(playlist_id, playlist_name, auth_key, tempdir)

    assert result.exit_code == 0
    files = sorted(os.listdir(tempdir))
    assert len(files) == 2
    assert files == sorted([diff_file, data_file])
    assert _read_file_lines(os.path.join(tempdir, diff_file)) == []
    data = _read_file_lines(os.path.join(tempdir, data_file))
    assert len(data) == 129


def test_existing_directory(tempdir: str, mock_api_calls, playlist_id: str, playlist_name: str, auth_key: str):
    diff_file = f"{playlist_name}YoutubeBackupDiff.txt"
    data_file = f"{playlist_name}YoutubeBackupNew.txt"
    diff_file_backup = f"{playlist_name}YoutubeBackupDiffOld.txt"
    data_file_backup = f"{playlist_name}YoutubeBackup.txt"
    open(os.path.join(tempdir, diff_file), "w", encoding="utf-8").close()
    changed_title = "TEST - CHANGED - TITLE"
    with open(os.path.join(tempdir, data_file), "w", encoding="utf-8") as f:
        f.writelines([
            "1. Mediterranean Sundance germany '81\n",
            f"2. {changed_title}\n",
            "3. Douchebags! Douchebags! Douchebags! (3/7/08)\n",
        ])

    result = _run_cli(playlist_id, playlist_name, auth_key, tempdir)

    assert result.exit_code == 0
    files = sorted(os.listdir(tempdir))
    assert len(files) == 4
    assert files == sorted([diff_file, data_file, data_file_backup, diff_file_backup])
    diff = _read_file_lines(os.path.join(tempdir, diff_file))
    assert diff == [
        f"128. Old: {changed_title}. New: Every dog has its day"
    ]
    data = _read_file_lines(os.path.join(tempdir, data_file))
    assert len(data) == 129


def _run_cli(playlist_id: str, playlist_name: str, auth_key: str, tempdir: str) -> Result:
    return runner.invoke(app, [
        "--playlist-id",
        playlist_id,
        "--youtube-auth-key",
        auth_key,
        "--playlist-name",
        playlist_name,
        "--output-dir",
        tempdir,
        "--new-videos-first"
    ])


def _read_test_resource(name: str) -> str:
    with open(os.path.join("data", name), encoding="utf-8") as f:
        return f.read()


def _read_file_lines(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return f.readlines()
