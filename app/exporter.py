import os.path
import shutil

from aiohttp import ClientSession

from app.apimodels import PlaylistItem
from app import utils
from app.options import Options
from app.retriever import PlaylistDataRetriever


class YouTubePlaylistExporter:
    def __init__(self, session: ClientSession, options: Options):
        self._session: ClientSession = session
        self._options: Options = options
        self._validate_input()
        self._new_version_path = self._get_path("YoutubeBackupNew")
        self._old_version_path = self._get_path("YoutubeBackup")
        self._diff_file_path = self._get_path("YoutubeBackupDiff")
        self._diff_backup_path = self._get_path("YoutubeBackupDiffOld")
        self._old_version_backup_path = self._get_path("YoutubeBackupOld")
        self._missing_videos_path = self._get_path("YoutubeMissingVideos")

    def _validate_input(self):
        if not os.path.isdir(self._options.output_dir):
            raise Exception(f"Supplied output folder {self._options.output_dir} doesn't exist")
        if not self._options.playlist_id:
            raise Exception("Must provide a non-empty playlist ID")
        # TODO more validations?

    def _get_path(self, suffix: str):
        return f"{os.path.join(self._options.output_dir, self._options.playlist_name)}-{suffix}.txt"

    async def export_playlist(self):
        new_items: list[PlaylistItem] = await PlaylistDataRetriever(self._session,
                                                                   self._options.playlist_id,
                                                                   self._options.youtube_auth_key).retrieve()
        prev_titles: list[str] = self._get_latest_backup_data()
        length_diff: int = self._calc_and_validate_length_diff(new_items, prev_titles)
        self._write_backup()
        self._override_old_files()
        self._write_new_titles(new_items)
        self._write_diff_file(new_items, prev_titles, length_diff)

    def _get_latest_backup_data(self) -> list[str]:
        utils.log(f"Retrieving old {self._options.playlist_name} data")
        path = self._new_version_path
        if not os.path.exists(path):
            return []
        return self._get_data_from_file(path)

    @staticmethod
    def _get_data_from_file(file_path: str) -> list[str]:
        with open(file_path, encoding="utf-8") as f:
            return [line[line.index(".") + 2:].strip() for line in f]

    def _calc_and_validate_length_diff(self, new_items: list[PlaylistItem], prev_titles: list[str]):
        utils.log("Validating new items and calculating diffs")
        num = len(new_items) - len(prev_titles)
        if num >= 0:
            return num
        self._create_missing_videos_file(new_items, prev_titles)
        raise Exception("Some videos were removed since the last run with no update to the files!")

    def _create_missing_videos_file(self, new_items: list[PlaylistItem], prev_titles: list[str]):
        new_titles = {item.snippet.title for item in new_items}
        with open(self._missing_videos_path, "w", encoding="utf-8") as f:
            for i in range(len(prev_titles)):
                if not prev_titles[i] in new_titles:
                    f.write(f"{i + 1}. {prev_titles[i]}\n")

    def _write_backup(self):
        utils.log("Creating backups")
        if os.path.exists(self._old_version_path):
            shutil.copyfile(self._old_version_path, self._old_version_backup_path)
        if os.path.exists(self._diff_file_path):
            shutil.copyfile(self._diff_file_path, self._diff_backup_path)

    def _override_old_files(self):
        if os.path.isfile(self._new_version_path):
            shutil.copyfile(self._new_version_path, self._old_version_path)

    def _write_new_titles(self, new_items: list[PlaylistItem]):
        utils.log(f"Writing new {self._options.playlist_name} titles to file")
        with open(self._new_version_path, "w", encoding="utf-8") as f:
            f.writelines([f"{i + 1}. {new_items[i].snippet.title}\n" for i in range(len(new_items))])

    def _write_diff_file(self, new_items: list[PlaylistItem], prev_titles: list[str], length_diff: int):
        utils.log("Writing diff file")
        with open(self._diff_file_path, "w", encoding="utf-8") as f:
            if self._options.are_new_videos_last:
                for i in range(len(prev_titles)):
                    prev_title = prev_titles[i]
                    new_title = new_items[i].snippet.title
                    if prev_title != new_title:
                        f.write(f"{i + 1}. Old: {prev_title}. New: {new_title}\n")
            else:
                for i in range(len(prev_titles) - 1, -1, -1):
                    prev_title = prev_titles[i]
                    new_title = new_items[i + length_diff].snippet.title
                    if prev_title != new_title:
                        f.write(f"{i + 1 + length_diff}. Old: {prev_title}. New: {new_title}\n")
